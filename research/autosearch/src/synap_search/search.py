from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
import math
import pickle
import hashlib
import time
import numpy as np
import optuna
from scipy.stats import spearmanr
from .config import ModelConfig, TrainConfig, DataConfig
from .io import read_json, write_json, write_bytes, digest, sha256, source_fingerprint, environment
from .training import train_trial


class DeterministicTPESampler(optuna.samplers.TPESampler):
    """Per-parameter deterministic TPE: partial Optuna suggestions replay exactly."""
    def __init__(self, seed=31001):
        super().__init__(seed=seed, n_startup_trials=6)
        self.base_seed = seed

    def sample_independent(self, study, trial, param_name, param_distribution):
        key = f"{self.base_seed}:{trial.number}:{param_name}"
        seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "little")
        sampler = optuna.samplers.TPESampler(seed=seed, n_startup_trials=6)
        return sampler.sample_independent(study, trial, param_name, param_distribution)


def feasible(metrics, reference):
    try:
        pairs = [(metrics["position"]["macro_f1"], reference["position"]["macro_f1"]),
                 (metrics["lesion"]["iou_at_0_5"], reference["lesion"]["iou_at_0_5"])]
        return all(math.isfinite(a) and math.isfinite(b) and a >= b for a, b in pairs)
    except (KeyError, TypeError):
        return False


def mean_metrics(results):
    metrics = [r["best"]["metrics"] for r in results]
    return {"r_final": float(np.mean([m["r_final"] for m in metrics])),
            "position": {"macro_f1": float(np.mean([m["position"]["macro_f1"] for m in metrics]))},
            "lesion": {"iou_at_0_5": float(np.mean([m["lesion"]["iou_at_0_5"] for m in metrics]))}}


def gate(config):
    output = Path(config["data"]["output"])
    if (output / "TEST_OPENED.json").exists() or (output / "FINAL_MANIFEST.json").exists():
        raise RuntimeError("Round is frozen or test opened; further search forbidden")
    audit = read_json(output / "DATA_AUDIT.json")
    if audit.get("status") != "PASS":
        raise RuntimeError("Data audit has not passed")
    for name, expected in audit["development_files"].items():
        if sha256(output / "development" / name) != expected:
            raise ValueError("Development data changed since audit")
    smoke = read_json(output / "SMOKE.json")
    if smoke.get("status") != "PASS" or smoke.get("source") != source_fingerprint():
        raise RuntimeError("Current code must pass smoke")
    if smoke.get("environment") != environment():
        raise RuntimeError("Smoke environment changed")
    if config["train"]["device"] == "cuda":
        real = smoke.get("gpu_real_batch")
        if not real or real["real_inner_train_images"] != config["train"]["batch_size"]:
            raise RuntimeError("Configured real CUDA batch has not passed smoke")
        if config["train"]["precision"] == "bf16" and not real.get("bf16_finite_loss_and_gradients"):
            raise RuntimeError("BF16 validation did not pass")
        if config["train"]["precision"] == "fp16":
            raise RuntimeError("FP16 search is not validated by current smoke")
    identity = {"config": config, "source": source_fingerprint(), "environment": environment(), "audit": digest(audit)}
    lock = output / "ROUND_LOCK.json"
    if lock.exists() and read_json(lock) != identity:
        raise ValueError("Round changed; strict resume denied")
    if not lock.exists():
        write_json(lock, identity)
    return output


def suggest_model(trial):
    name = trial.suggest_categorical("mechanism", ["M1", "M2", "M3", "M4", "G_slow"])
    if name == "G_slow":
        return ModelConfig(mechanism=name, auxiliary_eta=0)
    values = dict(mechanism=name, auxiliary_eta=trial.suggest_categorical("auxiliary_eta", [0., .1, .3, 1.]),
                  warmup=trial.suggest_categorical("warmup", [0, 10, 20]))
    if name != "M1":
        values.update(decoder=trial.suggest_categorical("decoder", ["c4", "fpn"]),
                      width=trial.suggest_categorical("width", [64, 128]), stride=trial.suggest_categorical("stride", [8, 4]))
    if name in {"M3", "M4"}:
        values.update(fusion=trial.suggest_categorical("fusion", ["feature", "logit", "experts"]),
                      injection_eta=trial.suggest_categorical("injection_eta", [0., .1, .3, 1.]))
    return ModelConfig(**values)


def suggest_recipe(trial, train, data, model):
    train = replace(train, lr=trial.suggest_float("lr", 3e-5, 3e-4, log=True),
                    weight_decay=trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True),
                    head_multiplier=trial.suggest_categorical("head_multiplier", [1, 3, 10]),
                    scheduler=trial.suggest_categorical("scheduler", ["step", "cosine"]),
                    ema=trial.suggest_categorical("ema", [0., .999]))
    data = replace(data, resize=trial.suggest_categorical("resize", ["stretch", "letterbox"]),
                   augmentation=trial.suggest_categorical("augmentation", ["legacy", "conservative"]))
    model = replace(model, loss=trial.suggest_categorical("loss", ["legacy", "cdf"]))
    if not model.mechanism.startswith("A_"):
        model = replace(model, position_weight=trial.suggest_categorical("position_weight", [.03, .1, .3]),
                        lesion_weight=trial.suggest_categorical("lesion_weight", [.03, .1, .3]),
                        warmup=trial.suggest_categorical("warmup", [0, 10, 20]))
    return model, train, data


def pruning_allowed(model, epoch, protected):
    return not protected and model.mechanism != "G_slow" and epoch in {30, 60} and epoch >= model.warmup + 10


def halving_decision(path, value, peers):
    """Persist the peer snapshot and decision together before changing trial state."""
    path = Path(path)
    if path.exists():
        return read_json(path)["prune"]
    values = sorted([float(v) for v in peers] + [float(value)])
    cutoff = values[max(0, math.ceil(len(values) / 2) - 1)]
    prune = value > cutoff
    write_json(path, {"peers": list(peers), "value": value, "cutoff": cutoff, "prune": prune})
    return prune


def calibration_reliability(output):
    histories = []
    for path in sorted((output / "mechanism").glob("trial_*/result.json")):
        if read_json(path)["completed_epoch"] == 120:
            histories.append(read_json(path.parent / "history.json"))
    if len(histories) < 6:
        return False
    correlations = []
    for rung in (30, 60):
        left = [min(r["r_final"] for r in h if 20 < r["epoch"] <= rung) for h in histories[:6]]
        right = [min(r["r_final"] for r in h if r["epoch"] > 20) for h in histories[:6]]
        value = float(spearmanr(left, right).statistic)
        correlations.append(value if math.isfinite(value) else None)
    passed = all(c is not None and c >= .5 for c in correlations)
    write_json(output / "PROXY_RELIABILITY.json", {"calibration_n": 6, "rungs": [30, 60], "spearman": correlations, "pruning_enabled": passed})
    return passed


def run_study(config, output, name, budget, reference, resume, structure=None):
    root = output / name
    root.mkdir(exist_ok=True)
    sampler_path = root / "sampler.pkl"
    sampler = pickle.loads(sampler_path.read_bytes()) if sampler_path.exists() else DeterministicTPESampler()
    study = optuna.create_study(study_name=name, storage="sqlite:///" + (root / "study.sqlite3").as_posix(),
                               direction="minimize", load_if_exists=resume, sampler=sampler,
                               pruner=optuna.pruners.SuccessiveHalvingPruner(min_resource=30, reduction_factor=2))
    if name == "mechanism" and not study.trials:
        for mechanism in ["M1", "M2", "M3", "M4", "G_slow", "M2"]:
            study.enqueue_trial({"mechanism": mechanism})
    while True:
        running = [t for t in study.trials if t.state == optuna.trial.TrialState.RUNNING]
        used = sum(t.state != optuna.trial.TrialState.WAITING for t in study.trials)
        if not running and used >= budget:
            break
        if len(running) > 1:
            raise RuntimeError("Unexpected concurrent trials")
        trial = optuna.Trial(study, running[0]._trial_id) if running else study.ask()
        directory = root / f"trial_{trial.number:03d}"
        proposal = directory / "proposal.json"
        train, data = TrainConfig(**config["train"]), DataConfig(**config["data"])
        if proposal.exists():
            saved = read_json(proposal)
            model, train, data = ModelConfig(**saved["model"]), TrainConfig(**saved["train"]), DataConfig(**saved["data"])
            study.sampler = pickle.loads(bytes.fromhex(saved["sampler_state"]))
        else:
            model = suggest_model(trial) if name == "mechanism" else structure or ModelConfig(mechanism="A_tuned")
            if name != "mechanism":
                model, train, data = suggest_recipe(trial, train, data, model)
            write_json(proposal, {"model": asdict(model), "train": asdict(train), "data": asdict(data),
                                 "sampler_state": pickle.dumps(study.sampler).hex()})
            write_bytes(sampler_path, pickle.dumps(study.sampler))
        protected = name != "mechanism" or trial.number < 6 or not calibration_reliability(output)
        def callback(epoch, best, history):
            if epoch in {30, 60, 120}:
                trial.report(best["metrics"]["r_final"], epoch)
                if pruning_allowed(model, epoch, protected):
                    peers = [t.intermediate_values[epoch] for t in study.trials if t.number != trial.number and epoch in t.intermediate_values]
                    if halving_decision(directory / f"rung_{epoch}.json", best["metrics"]["r_final"], peers):
                        raise optuna.TrialPruned()
        started = time.perf_counter()
        try:
            result = train_trial(config, model, train, data, directory, resume=resume, callback=callback)
            ok = model.mechanism.startswith("A_") or feasible(result["best"]["metrics"], reference)
            trial.set_user_attr("feasible", ok)
            trial.set_user_attr("result", str(directory / "result.json"))
            study.tell(trial, result["best"]["metrics"]["r_final"])
        except optuna.TrialPruned:
            trial.set_user_attr("feasible", False)
            write_json(directory / "status.json", {"status": "PRUNED", "auxiliary_feasibility": "not established"})
            study.tell(trial, state=optuna.trial.TrialState.PRUNED)
        except (FloatingPointError, ValueError, torch_cuda_oom()) as exc:
            write_json(directory / "failure.json", {"type": type(exc).__name__, "error": str(exc), "attempt_seconds": time.perf_counter() - started})
            study.tell(trial, state=optuna.trial.TrialState.FAIL)
            if not isinstance(exc, (FloatingPointError, torch_cuda_oom())):
                raise
        except Exception as exc:
            write_json(directory / "interruption.json", {"type":type(exc).__name__, "error":str(exc),
                       "status":"INFRASTRUCTURE_INTERRUPTION", "attempt_seconds":time.perf_counter()-started})
            raise
        finally:
            write_bytes(sampler_path, pickle.dumps(study.sampler))
            write_json(root / "trial_registry.json", [{"number": t.number, "state": t.state.name, "params": t.params, "attributes": t.user_attrs, "value": t.value} for t in study.trials])
    valid = [read_json(t.user_attrs["result"]) for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE and t.user_attrs.get("feasible")]
    valid.sort(key=lambda r: r["best"]["key"])
    write_json(root / "leaderboard_120.json", valid)
    return valid


def torch_cuda_oom():
    import torch
    return torch.cuda.OutOfMemoryError


def search(config, resume=False):
    output = gate(config)
    train, data = TrainConfig(**config["train"]), DataConfig(**config["data"])
    reference = train_trial(config, ModelConfig(mechanism="E_reference"), train, data, output / "controls/E_reference", resume=resume)
    write_json(output / "AUX_REFERENCE.json", reference)
    baseline = run_study(config, output, "baseline", 8, None, resume)
    mechanisms = run_study(config, output, "mechanism", 24, reference["best"]["metrics"], resume)
    if not baseline or not mechanisms:
        write_json(output / "SEARCH_COMPLETE.json", {"status": "NO_FEASIBLE_CANDIDATE"})
        return {"status": "NO_FEASIBLE_CANDIDATE"}
    tuned = run_study(config, output, "recipe", 8, reference["best"]["metrics"], resume, ModelConfig(**mechanisms[0]["model"]))
    pool = sorted(mechanisms + tuned, key=lambda r: r["best"]["key"])
    chosen, identities = [], set()
    for result in pool:
        key = digest({k: result[k] for k in ("model", "train", "data")})
        if key not in identities:
            chosen.append(result)
            identities.add(key)
        if len(chosen) == 2:
            break
    result = {"status": "COMPLETE" if len(chosen) == 2 else "NO_FEASIBLE_CANDIDATE", "baseline": baseline[0], "candidates": chosen}
    write_json(output / "SEARCH_COMPLETE.json", result)
    return result


def confirm(config, resume=True):
    output = gate(config)
    selected = read_json(output / "SEARCH_COMPLETE.json")
    if selected["status"] != "COMPLETE":
        raise RuntimeError("No feasible shortlist")
    defaults = {"train": config["train"], "data": config["data"]}
    tasks = {"A_legacy": {**defaults, "model": asdict(ModelConfig(mechanism="A_legacy"))},
             "E_reference": {**defaults, "model": asdict(ModelConfig(mechanism="E_reference"))},
             "A_tuned": selected["baseline"], **{f"candidate_{i+1}": r for i, r in enumerate(selected["candidates"])}}
    results = {}
    for name, task in tasks.items():
        results[name] = []
        for seed in config["search"]["seeds"]:
            result = train_trial(config, ModelConfig(**task["model"]), replace(TrainConfig(**task["train"]), seed=seed),
                                 DataConfig(**task["data"]), output / "confirmation" / name / str(seed), native=True, resume=resume)
            results[name].append(result)
    reference = mean_metrics(results["E_reference"])
    feasible_names = [name for name in ("candidate_1", "candidate_2") if feasible(mean_metrics(results[name]), reference)]
    winner = min(feasible_names, key=lambda name: (mean_metrics(results[name])["r_final"], name)) if feasible_names else None
    report = {"status": "COMPLETE" if winner else "NO_FEASIBLE_CANDIDATE", "winner": winner, "results": results}
    write_json(output / "CONFIRM_COMPLETE.json", report)
    return report
