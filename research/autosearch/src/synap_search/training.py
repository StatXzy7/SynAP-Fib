from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import math
import random
import time
import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader
from sfibai_b.data import EpochShuffleSampler
from sfibai_b.prediction import PredictionCollector
from sfibai_b.evaluation import evaluate_predictions, checkpoint_key
from sfibai_b.storage import save_prediction_bundle
from .config import ModelConfig, DataConfig, TrainConfig
from .data import DevelopmentDataset, predicted_regions
from .models import SearchModel, SearchObjective
from .io import digest, environment, read_json, write_json, save_checkpoint, sha256, source_fingerprint


def loader(dataset, config, training):
    sampler = EpochShuffleSampler(size=len(dataset), seed=config.seed) if training else None
    options = dict(batch_size=config.batch_size, sampler=sampler, num_workers=config.workers,
                   pin_memory=config.device == "cuda", drop_last=False,
                   generator=torch.Generator().manual_seed(config.seed))
    if config.workers:
        options.update(persistent_workers=True, prefetch_factor=2)
    return DataLoader(dataset, **options), sampler


def learning_rate_factor(epoch, config):
    if config.scheduler == "step":
        return .6 ** ((epoch - 1) // 15)
    if epoch <= 5:
        return epoch / 5
    return .5 * (1 + math.cos(math.pi * (epoch - 5) / (120 - 5)))


def rng_state():
    return {"torch": torch.get_rng_state(), "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
            "numpy": np.random.get_state(), "python": random.getstate()}


def restore_rng(state):
    torch.set_rng_state(state["torch"])
    if state["cuda"]:
        torch.cuda.set_rng_state_all(state["cuda"])
    np.random.set_state(state["numpy"])
    random.setstate(state["python"])


@torch.no_grad()
def infer(model, batches, config, full=False):
    model.eval()
    collector = PredictionCollector(arm="MTL" if model.has_aux else "A", full=full, collect_attention=full and model.has_aux)
    native_collector = PredictionCollector(arm="MTL", full=False, collect_attention=False) if model.has_aux else None
    regions = []
    device = torch.device(config.device)
    for batch in batches:
        with torch.autocast(device.type, dtype=torch.bfloat16 if config.precision == "bf16" else torch.float16,
                            enabled=config.precision != "fp32"):
            outputs = model(batch["image"].to(device, non_blocking=True))
        if not all(torch.isfinite(t).all() for t in outputs.values()):
            raise FloatingPointError("Nonfinite inference output")
        if model.has_aux:
            native_collector.add_batch(batch, outputs)
            if full:
                for i, uid in enumerate(batch["image_uid"]):
                    regions.append({"image_uid": uid, "regions": predicted_regions(outputs["lesion_attention"][i, 0].cpu().numpy(), batch["inverse"][i].numpy(), batch["image"].shape[-1], batch["roi_shape"][i].tolist())})
            # Predeclared canonical 32x32 grid at 512 input. Resample probabilities.
            outputs = dict(outputs)
            outputs["lesion_attention"] = F.interpolate(outputs["lesion_attention"].float(), size=(32, 32), mode="area")
        collector.add_batch(batch, outputs)
    frame = collector.to_frame()
    if len(frame) != len(batches.dataset):
        raise ValueError("Incomplete inference")
    metrics = evaluate_predictions(frame)
    if model.has_aux:
        native = native_collector.to_frame()
        valid = native.lesion_valid.astype(bool)
        metrics["native_resolution_weak_box"] = {k: float(native.loc[valid, k].mean()) if valid.any() else None for k in ("dice_at_0_5", "iou_at_0_5")}
        confusion = np.zeros((6, 6), dtype=int)
        for true, pred in zip(frame.position_true, frame.position_pred):
            confusion[int(true) - 1, int(pred) - 1] += 1
        metrics["position"]["confusion_matrix"] = confusion.tolist()
    return frame, metrics, collector.attention_payload(), regions


def make_datasets(config, train_config, data_config, native=False):
    root = Path(config["data"]["output"]) / "development"
    names = ("native_train", "native_val") if native else ("inner_train", "inner_val")
    return [DevelopmentDataset(root=data_config.root, manifest=root / "images.csv", annotations=root / f"{name}.jsonl",
                               partition=name, config=data_config, seed=train_config.seed, training=(i == 0)) for i, name in enumerate(names)]


def train_trial(config, model_config, train_config, data_config, directory, *, native=False, target_epoch=120, resume=False, callback=None):
    if not 1 <= target_epoch <= 120:
        raise ValueError("Invalid resource horizon")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    audit = read_json(Path(config["data"]["output"]) / "DATA_AUDIT.json")
    identity = {"model": asdict(model_config), "train": asdict(train_config), "data": asdict(data_config), "native": native,
                "development": audit["development_files"], "source": source_fingerprint(), "environment": environment()}
    identity_hash = digest(identity)
    if (directory / "identity.json").exists():
        if read_json(directory / "identity.json") != identity:
            raise ValueError("Strict resume rejected changed configuration/data/code/environment")
        if not resume:
            raise ValueError("Trial already exists; use strict resume")
    else:
        write_json(directory / "identity.json", identity)
    if (directory / "result.json").exists():
        result = read_json(directory / "result.json")
        if sha256(directory / "best.pt") != result["checkpoint_sha256"]:
            raise ValueError("Completed checkpoint changed")
        if result["completed_epoch"] >= target_epoch:
            return result
    torch.manual_seed(train_config.seed)
    random.seed(train_config.seed)
    np.random.seed(train_config.seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.set_num_threads(4)
    device = torch.device(train_config.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA not available")
    if train_config.precision == "bf16" and (device.type != "cuda" or not torch.cuda.is_bf16_supported()):
        raise ValueError("BF16 requires validated supporting hardware")
    train_dataset, valid_dataset = make_datasets(config, train_config, data_config, native)
    train_loader, sampler = loader(train_dataset, train_config, True)
    val_loader, _ = loader(valid_dataset, train_config, False)
    model = SearchModel(model_config, train_config.seed, train_config.pretrained).to(device)
    objective = SearchObjective(model_config)
    backbone = list(model.base.backbone.parameters())
    backbone_ids = {id(p) for p in backbone}
    heads = [p for p in model.parameters() if id(p) not in backbone_ids]
    optimizer = torch.optim.AdamW([{"params": backbone, "lr": train_config.lr}, {"params": heads, "lr": train_config.lr * train_config.head_multiplier}], weight_decay=train_config.weight_decay)
    scaler = torch.amp.GradScaler(device.type, enabled=train_config.precision == "fp16", init_scale=1024)
    ema = deepcopy(model).eval() if train_config.ema else None
    if ema is not None:
        ema.requires_grad_(False)
    history, completed, best, elapsed = [], 0, None, 0.
    if resume and (directory / "last.pt").exists():
        saved = torch.load(directory / "last.pt", map_location="cpu", weights_only=False)
        if saved["identity"] != identity_hash:
            raise ValueError("Checkpoint identity mismatch")
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        scaler.load_state_dict(saved["scaler"])
        if ema is not None:
            ema.load_state_dict(saved["ema"])
        history, completed, best, elapsed = saved["history"], saved["epoch"], saved["best"], saved["elapsed_seconds"]
        restore_rng(saved["rng"])
    start = time.perf_counter()
    for epoch in range(completed + 1, target_epoch + 1):
        sampler.set_epoch(epoch)
        objective.set_epoch(epoch)
        factor = learning_rate_factor(epoch, train_config)
        for group, multiplier in zip(optimizer.param_groups, [1, train_config.head_multiplier]):
            group["lr"] = train_config.lr * multiplier * factor
        model.train()
        losses, steps, skipped, grad_norm = 0., 0, 0, 0.
        for cpu_batch in train_loader:
            batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in cpu_batch.items()}
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device.type, dtype=torch.bfloat16 if train_config.precision == "bf16" else torch.float16, enabled=train_config.precision != "fp32"):
                outputs = model(batch["image"])
            with torch.autocast(device.type, enabled=False):
                loss = objective.loss_components(outputs, batch)["total"]
            if not torch.isfinite(loss):
                raise FloatingPointError("Nonfinite training loss")
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            finite = all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
            if not finite and train_config.precision != "fp16":
                raise FloatingPointError("Nonfinite gradient")
            if steps == 0 and finite:
                grad_norm = float(torch.sqrt(sum(p.grad.float().square().sum() for p in backbone if p.grad is not None)))
            before = scaler.get_scale()
            scaler.step(optimizer)
            scaler.update()
            did_skip = scaler.get_scale() < before
            skipped += int(did_skip)
            if ema is not None and not did_skip:
                with torch.no_grad():
                    current = model.state_dict()
                    for key, value in ema.state_dict().items():
                        if value.is_floating_point():
                            value.lerp_(current[key], 1 - train_config.ema)
                        else:
                            value.copy_(current[key])
            losses += float(loss.detach())
            steps += 1
        frame, metrics, _, _ = infer(ema or model, val_loader, train_config)
        key = checkpoint_key(metrics, epoch)
        improved = epoch > 20 and (best is None or key < tuple(best["key"]))
        if improved:
            best = {"key": list(key), "metrics": metrics, "epoch": epoch}
            save_checkpoint(directory / "best.pt", {"model": (ema or model).state_dict(), "identity": identity_hash, "epoch": epoch})
            save_prediction_bundle(directory=directory / "best_val", frame=frame, metrics=metrics, attention=None, full=False)
        row = {"epoch": epoch, "train_loss": losses / steps, "r_final": metrics["r_final"],
               "metrics": metrics, "lr": optimizer.param_groups[0]["lr"], "aux_scale": objective.base.aux_scale,
               "backbone_grad_norm": grad_norm, "overflow_skipped": skipped}
        history.append(row)
        seconds = elapsed + time.perf_counter() - start
        save_checkpoint(directory / "last.pt", {"identity": identity_hash, "model": model.state_dict(), "optimizer": optimizer.state_dict(),
                        "scaler": scaler.state_dict(), "ema": ema.state_dict() if ema is not None else None,
                        "rng": rng_state(), "epoch": epoch, "history": history, "best": best, "elapsed_seconds": seconds})
        write_json(directory / "history.json", history)
        write_json(directory / "status.json", {"status": "RUNNING", "epoch": epoch, "elapsed_seconds": seconds})
        print(f"{directory.name}: epoch={epoch} dev_R_final={metrics['r_final']:.6f}", flush=True)
        if callback:
            callback(epoch, best or {"metrics": metrics}, history)
    if best is None:
        raise RuntimeError("No eligible checkpoint; not a completed trial")
    result = {"completed_epoch": target_epoch, "best": best, "identity": identity_hash,
              "checkpoint": str((directory / "best.pt").resolve()), "checkpoint_sha256": sha256(directory / "best.pt"),
              "elapsed_seconds": elapsed + time.perf_counter() - start,
              "parameters": sum(p.numel() for p in model.parameters()),
              "peak_memory_bytes": torch.cuda.max_memory_allocated() if device.type == "cuda" else None,
              "model": asdict(model_config), "train": asdict(train_config), "data": asdict(data_config)}
    write_json(directory / "result.json", result)
    write_json(directory / "status.json", {"status": "COMPLETE", "epoch": target_epoch})
    return result
