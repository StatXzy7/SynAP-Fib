"""Independent final evaluation. Imported only by freeze/final-test/report."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import math
import json
import time
import numpy as np
import pandas as pd
import torch
from sfibai_b.storage import save_prediction_bundle
from sfibai_b.protocol import MANIFEST_SHA256, ANNOTATIONS_SHA256
from .config import ModelConfig, TrainConfig, DataConfig
from .data import DevelopmentDataset
from .models import SearchModel
from .io import digest, read_json, write_json, sha256, source_fingerprint, environment
from .training import infer, loader


def freeze(config):
    root = Path(config["data"]["output"])
    path = root / "FINAL_MANIFEST.json"
    if path.exists():
        verify_manifest(path)
        return {"status": "FROZEN", "manifest": str(path)}
    from .search import gate
    gate(config)
    confirm = read_json(root / "CONFIRM_COMPLETE.json")
    if confirm["status"] != "COMPLETE" or not confirm["winner"]:
        raise RuntimeError("No feasible final candidate; test stays closed")
    chosen = {name: confirm["results"][name] for name in ("A_legacy", "A_tuned", "E_reference", confirm["winner"])}
    for name, results in chosen.items():
        if [r["train"]["seed"] for r in results] != [34001, 34002, 34003]:
            raise ValueError("Missing or reordered confirmation seeds")
        for result in results:
            if result["completed_epoch"] != 120 or not 20 < result["best"]["epoch"] <= 120:
                raise ValueError("Incomplete training or invalid checkpoint selection")
            if sha256(result["checkpoint"]) != result["checkpoint_sha256"]:
                raise ValueError("Checkpoint changed")
    payload = {"status": "FROZEN", "round": config["round"], "historical_test_exposure": True,
               "primary_comparison": [confirm["winner"], "A_tuned"], "results": chosen,
               "seeds": [34001, 34002, 34003], "config": config,
               "source": source_fingerprint(), "environment": environment(),
               "audit": read_json(root / "DATA_AUDIT.json"), "confirmation_sha256": sha256(root / "CONFIRM_COMPLETE.json"),
               "inference": {"threshold": 0.5, "components": "8-connected", "canonical_grid": [32, 32],
                             "heatmap_resize": "area_probability", "calibration": None, "ensemble": None,
                             "three_heads_enabled": True}, "bootstrap": {"resamples": 10000, "seed": 35001}}
    payload["sha256"] = digest(payload)
    write_json(path, payload)
    write_json(root / "FREEZE_RECEIPT.json", {"manifest_sha256": sha256(path)})
    verify_manifest(path)
    return {"status": "FROZEN", "manifest": str(path)}


def verify_manifest(path):
    path = Path(path).resolve()
    manifest = read_json(path)
    claimed = manifest.pop("sha256", None)
    if claimed != digest(manifest) or manifest.get("status") != "FROZEN":
        raise ValueError("Manifest hash or frozen status invalid")
    if read_json(path.parent / "FREEZE_RECEIPT.json")["manifest_sha256"] != sha256(path):
        raise ValueError("Manifest differs from freeze receipt")
    if manifest["source"] != source_fingerprint() or manifest["environment"] != environment():
        raise ValueError("Frozen source/environment changed; new round required")
    if manifest["seeds"] != [34001, 34002, 34003] or len(manifest["results"]) != 4:
        raise ValueError("Incomplete comparison manifest")
    for results in manifest["results"].values():
        if [r["train"]["seed"] for r in results] != manifest["seeds"]:
            raise ValueError("Missing seed")
        for result in results:
            if sha256(result["checkpoint"]) != result["checkpoint_sha256"]:
                raise ValueError("Frozen checkpoint hash mismatch")
    manifest["sha256"] = claimed
    return manifest


def test_dataset(manifest, data_config, private):
    # Build test-only files exclusively after a verified final freeze.
    root = Path(data_config.root)
    native = root / "manifests/images.csv"
    annotations = root / "manifests/annotations.jsonl"
    if sha256(native) != MANIFEST_SHA256 or sha256(annotations) != ANNOTATIONS_SHA256:
        raise ValueError("Native data fingerprints changed")
    frame = pd.read_csv(native, dtype=str, encoding="utf-8")
    frame = frame.loc[frame.split == "test"].copy()
    if (len(frame), frame.patient_uid.nunique(), frame.center_id.nunique()) != (4107, 240, 4):
        raise ValueError("Incorrect native test cardinality")
    for row in frame.itertuples(index=False):
        from .data import safe_image_path
        if sha256(safe_image_path(root, row.image_path, "test")) != row.image_hash_v2:
            raise ValueError("Test image changed since audit")
    private.mkdir(parents=True, exist_ok=True)
    uids = set(frame.image_uid)
    target = private / "annotations.jsonl"
    with target.open("w", encoding="utf-8") as out, annotations.open(encoding="utf-8") as handle:
        for line in handle:
            if json.loads(line)["image_uid"] in uids:
                out.write(line)
    obj = DevelopmentDataset.__new__(DevelopmentDataset)
    obj._initialize(root, frame.assign(split="train"), target, "native_train", data_config, 0, False)
    obj.split = "test"
    obj.frame["split"] = "test"
    return obj


def final_test(path):
    path = Path(path).resolve()
    manifest = verify_manifest(path)
    root = path.parent
    write_json(root / "TEST_OPENED.json", {"manifest_sha256": manifest["sha256"], "search_closed": True})
    for name, results in manifest["results"].items():
        for result in results:
            directory = root / "final_test" / name / str(result["train"]["seed"])
            completion = directory / "COMPLETE.json"
            if completion.exists():
                record = read_json(completion)
                if record["checkpoint_sha256"] != result["checkpoint_sha256"]:
                    raise ValueError("Completed test bundle changed checkpoint")
                for file, fingerprint in record["files"].items():
                    if sha256(directory / file) != fingerprint:
                        raise ValueError("Completed test bundle corrupted")
                continue
            config = TrainConfig(**result["train"])
            dataset = test_dataset(manifest, DataConfig(**result["data"]), root / "final_test/private")
            batches, _ = loader(dataset, config, False)
            model = SearchModel(ModelConfig(**result["model"]), config.seed, pretrained=False).to(config.device)
            checkpoint = torch.load(result["checkpoint"], map_location="cpu", weights_only=False)
            model.load_state_dict(checkpoint["model"])
            frame, metrics, attention, regions = infer(model, batches, config, full=True)
            from .data import predicted_regions
            # Same batch1 decode-to-host-output measurement with all available heads.
            durations = []
            model.eval()
            with torch.no_grad():
                for iteration in range(12):
                    if config.device == "cuda":
                        torch.cuda.synchronize()
                    started = time.perf_counter()
                    sample = dataset[iteration % len(dataset)]
                    with torch.autocast(config.device, dtype=torch.bfloat16 if config.precision == "bf16" else torch.float16, enabled=config.precision != "fp32"):
                        prediction = model(sample["image"].unsqueeze(0).to(config.device))
                    posterior = prediction["logits"].float().softmax(1).cpu()
                    if model.has_aux:
                        prediction["position_probs"].cpu()
                        predicted_regions(prediction["lesion_attention"][0, 0].float().cpu().numpy(), sample["inverse"].numpy(), sample["image"].shape[-1], sample["roi_shape"].tolist())
                    if config.device == "cuda":
                        torch.cuda.synchronize()
                    if iteration >= 2:
                        durations.append(time.perf_counter() - started)
            metrics["cost"] = {"parameters": result["parameters"], "training_seconds": result["elapsed_seconds"],
                               "training_peak_memory_bytes": result["peak_memory_bytes"],
                               "batch1_decode_to_outputs_median_ms": 1000 * float(np.median(durations)),
                               "latency_repetitions": 10, "all_available_heads_enabled": True}
            save_prediction_bundle(directory=directory, frame=frame, metrics=metrics, attention=attention, full=True)
            write_json(directory / "regions.json", regions)
            write_json(directory / "deployment.json", {"checkpoint": result["checkpoint"], "checkpoint_sha256": result["checkpoint_sha256"],
                       "model": result["model"], "preprocessing": result["data"], "inference": manifest["inference"]})
            files = {p.name: sha256(p) for p in directory.iterdir() if p.is_file() and p.name != "COMPLETE.json"}
            write_json(completion, {"checkpoint_sha256": result["checkpoint_sha256"], "files": files})
    return {"status": "COMPLETE", "manifest": str(path)}


def paired_seed_bootstrap(candidates, references, resamples=10000, seed=35001):
    from sfibai_b.bootstrap import _validate_pair, _cluster_table, _observed_r_final
    if len(candidates) != 3 or len(references) != 3:
        raise ValueError("Exactly three paired seeds required")
    for candidate, reference in zip(candidates, references):
        _validate_pair(candidate, reference)
        _validate_pair(candidate, candidates[0])
    pairs = [(_cluster_table(a), _cluster_table(b)) for a, b in zip(candidates, references)]
    clusters = pairs[0][0]
    centers = sorted(clusters.center_id.unique())
    rng = np.random.default_rng(seed)
    draws_by_center = [np.flatnonzero(clusters.center_id.to_numpy() == c) for c in centers]
    delta = np.zeros((3, resamples))
    image_counts = clusters.image_count.to_numpy()
    total_patients = len(clusters)
    total_weight = sum(math.sqrt(len(idx)) for idx in draws_by_center)
    risk_img = np.zeros((3, resamples))
    risk_patient = np.zeros((3, resamples))
    risk_center = np.zeros((3, resamples))
    n_images = np.zeros(resamples)
    for indices in draws_by_center:
        draws = indices[rng.integers(0, len(indices), size=(resamples, len(indices)))]
        n_images += image_counts[draws].sum(1)
        for s, (candidate, reference) in enumerate(pairs):
            risk_img[s] += (candidate.image_risk_sum.to_numpy()[draws] - reference.image_risk_sum.to_numpy()[draws]).sum(1)
            pr = candidate.patient_risk.to_numpy()[draws] - reference.patient_risk.to_numpy()[draws]
            risk_patient[s] += pr.sum(1)
            risk_center[s] += math.sqrt(len(indices)) * pr.mean(1)
    delta = .4 * risk_img / n_images + .4 * risk_patient / total_patients + .2 * risk_center / total_weight
    mean = delta.mean(0)
    observed = [_observed_r_final(a) - _observed_r_final(b) for a, b in pairs]
    return {"paired_deltas": observed, "mean_delta": float(np.mean(observed)), "sample_sd": float(np.std(observed, ddof=1)),
            "directions": ["lower" if x < 0 else "higher" if x > 0 else "equal" for x in observed],
            "ci95": np.percentile(mean, [2.5, 97.5]).tolist(), "resamples": resamples,
            "conditional_on_fixed_seeds": True, "resampling_unit": "center_stratified_patient_cluster"}


def report(path=None, config=None):
    root = Path(path).resolve().parent if path else Path(config["data"]["output"])
    lines = ["# Test set 主结果", "", "TEST PENDING / 结果未完成。Test 未执行或产物尚不完整。", "",
             "预锁定主终点：R_final = 0.4 image COR + 0.4 patient-max COR + 0.2 sqrt(center n) 加权 patient-max COR；越低越好。",
             "本轮固定 seeds: 34001, 34002, 34003。历史 test 已有暴露；本轮搜索阶段隔离 test。", ""]
    if path:
        manifest = verify_manifest(path)
        frames, all_metrics = {}, {}
        complete = True
        for name, results in manifest["results"].items():
            frames[name], all_metrics[name] = [], []
            for result in results:
                directory = root / "final_test" / name / str(result["train"]["seed"])
                if not (directory / "COMPLETE.json").exists():
                    complete = False
                    continue
                frames[name].append(pd.read_csv(directory / "predictions_full.csv.gz", dtype={"image_uid": str, "patient_uid": str, "center_id": str}))
                all_metrics[name].append(read_json(directory / "metrics.json"))
        if complete:
            from .search import feasible
            winner = manifest["primary_comparison"][0]
            bootstrap = paired_seed_bootstrap(frames[winner], frames["A_tuned"])
            write_json(root / "PAIRED_BOOTSTRAP.json", bootstrap)
            lines[2] = "Test 已执行。4,107 images / 240 patients / 4 centers；comparison round: synap-autosearch-v1；全部模型在 test 前冻结。"
            ranking = sorted(all_metrics, key=lambda n: np.mean([m["r_final"] for m in all_metrics[n]]))
            lines += ["| 模型 | seed34001 | seed34002 | seed34003 | mean ± sample SD |", "|---|---:|---:|---:|---:|"]
            for name in ranking:
                values = [m["r_final"] for m in all_metrics[name]]
                lines.append(f"| {name} | {values[0]:.6f} | {values[1]:.6f} | {values[2]:.6f} | {np.mean(values):.6f} ± {np.std(values, ddof=1):.6f} |")
            lines += ["", "主要配对比较：", "```json", json.dumps(bootstrap, ensure_ascii=False, indent=2), "```"]
            for name, metrics in all_metrics.items():
                lines += ["", f"## {name} 全部 test 指标", "```json", json.dumps(metrics, ensure_ascii=False, indent=2), "```"]
    lines += ["", "## 开发集结果与 checkpoint 选择", ""]
    for label in ("SEARCH_COMPLETE.json", "CONFIRM_COMPLETE.json"):
        if (root / label).exists():
            state = read_json(root / label)
            lines.append(f"{label}: {state['status']}。详见同目录结构化记录。")
        else:
            lines.append(f"{label}: 未完成；无可报告的正式开发排名。")
    lines += ["", "## 限制", "", "弱框指标是 weak-box agreement；真实轮廓分割与外部临床效用未独立验证。",
              "未完成的训练、确认或 test 均不构成性能提升证据。成本、环境、源代码和数据指纹保存在各 trial identity/result、ENVIRONMENT、DATA_AUDIT 与 ROUND_LOCK 文件。"]
    target = root / "FINAL_REPORT.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"report": str(target)}
