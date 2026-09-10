from __future__ import annotations

from pathlib import Path
import gc
import time
import torch
from .models import SearchModel, SearchObjective, image_outputs
from .config import ModelConfig, TrainConfig, DataConfig
from .io import write_json, source_fingerprint, environment
from .training import make_datasets, loader


def synthetic_batch(size=64, device="cpu"):
    generator = torch.Generator().manual_seed(7)
    mask = torch.zeros(2, 1, size, size, device=device)
    mask[:, :, size//4:3*size//4, size//4:3*size//4] = 1
    return {"image": torch.randn(2, 3, size, size, generator=generator).to(device),
            "label_bin": torch.tensor([4, 25], device=device), "position_norm": torch.tensor([1, 6], device=device),
            "lesion_mask": mask, "lesion_box_valid": torch.ones(2, dtype=torch.bool, device=device),
            "local_target": torch.where(mask > 0, mask * 4, -torch.ones_like(mask))}


def gradient_matrix(model, batch):
    objective = SearchObjective(model.config)
    groups = {"backbone": model.base.backbone, "grading": model.base.grading_head,
              "position": model.base.position_head,
              "lesion": model.decoder if hasattr(model, "decoder") else model.base.lesion_head}
    for name in ("position_residual", "position_gate", "lesion_residual", "lesion_gate"):
        if hasattr(model.base,name):
            groups[name]=getattr(model.base,name)
    for name in ("fusion", "experts", "local_severity"):
        if hasattr(model,name):
            groups[name]=getattr(model,name)
    result, vectors = {}, {}
    for loss in ("grading", "position", "box_raw"):
        model.zero_grad(set_to_none=True)
        values = objective.loss_components(model(batch["image"]), batch)
        values[loss].backward()
        result[loss] = {name: float(sum(p.grad.detach().square().sum() for p in module.parameters() if p.grad is not None).sqrt())
                        if any(p.grad is not None for p in module.parameters()) else 0. for name, module in groups.items()}
        vectors[loss] = torch.cat([(p.grad.detach().flatten() if p.grad is not None else torch.zeros_like(p).flatten()) for p in model.base.backbone.parameters()])
    cosine = {}
    for loss in ("position", "box_raw"):
        a, b = vectors["grading"], vectors[loss]
        cosine[loss] = float(torch.nn.functional.cosine_similarity(a[None], b[None])) if a.norm() > 0 and b.norm() > 0 else None
    return {"norms": result, "grading_auxiliary_cosine": cosine}


def smoke(config):
    torch.set_num_threads(4)
    output = Path(config["data"]["output"])
    batch = synthetic_batch()
    specs = [ModelConfig(mechanism="E_reference"), ModelConfig(mechanism="M1", auxiliary_eta=0),
             ModelConfig(mechanism="M1", auxiliary_eta=.3), ModelConfig(mechanism="M2", decoder="fpn"),
             ModelConfig(mechanism="M3", fusion="feature", injection_eta=0),
             ModelConfig(mechanism="M3", fusion="logit", injection_eta=1),
             ModelConfig(mechanism="M4", fusion="experts", decoder="fpn", injection_eta=.3)]
    matrices = []
    for spec in specs:
        model = SearchModel(spec, 31001).eval()
        result = image_outputs(model, batch["image"])
        assert result["probabilities"].shape == (2, 36)
        assert result["position_probabilities"].shape == (2, 6)
        assert torch.allclose(result["probabilities"].sum(1), torch.ones(2), atol=1e-6)
        assert ((result["score"] >= 0) & (result["score"] <= 3.5)).all()
        matrices.append({"mechanism": spec.mechanism, "auxiliary_eta": spec.auxiliary_eta, "injection_eta": spec.injection_eta,
                         **gradient_matrix(model, batch)})
        del model, result
        gc.collect()
    write_json(output / "GRADIENT_TOPOLOGY.json", {"evidence": "synthetic FP32 batch; mechanics only, no performance claim", "matrices": matrices})
    gpu = None
    if torch.cuda.is_available() and (output / "development/images.csv").exists():
        cfg = TrainConfig(**config["train"])
        datasets = make_datasets(config, cfg, DataConfig(**config["data"]))
        batches, sampler = loader(datasets[0], cfg, True)
        sampler.set_epoch(1)
        real = next(iter(batches))
        real = {k: v.cuda() if isinstance(v, torch.Tensor) else v for k, v in real.items()}
        model = SearchModel(ModelConfig(mechanism="M4", decoder="fpn", width=128, stride=4, fusion="experts", injection_eta=.3), 31001).cuda().train()
        objective = SearchObjective(model.config)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        for _ in range(2):
            optimizer.zero_grad(set_to_none=True)
            values = objective.loss_components(model(real["image"]), real)
            assert torch.isfinite(values["total"])
            values["total"].backward()
            assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
            optimizer.step()
        torch.cuda.synchronize()
        gpu = {"real_inner_train_images": len(real["image"]), "updates": 2, "precision": "fp32", "seconds": time.perf_counter() - start,
               "peak_bytes": torch.cuda.max_memory_allocated(), "source": "native inner train only"}
        # BF16 forward/backward stability is separately measured, not silently enabled.
        if torch.cuda.is_bf16_supported():
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                outputs = model(real["image"])
            loss = objective.loss_components(outputs, real)["total"]
            loss.backward()
            gpu["bf16_finite_loss_and_gradients"] = bool(torch.isfinite(loss) and all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()))
        del model, optimizer, real
        torch.cuda.empty_cache()
    record = {"status": "PASS", "source": source_fingerprint(), "environment": environment(), "cpu_shape_gradient_smoke": True,
              "gpu_real_batch": gpu, "performance_results": None}
    write_json(output / "SMOKE.json", record)
    return record
