"""Independent data auditor. Never imports the search controller or scores models."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import math
import subprocess
import cv2
import numpy as np
import pandas as pd
from sfibai_b.data import validate_data_v4, FormalImageDataset
from .data import inner_partition, safe_image_path
from .io import sha256, write_json, environment, source_fingerprint, digest


def audit(config):
    output = Path(config["data"]["output"])
    output.mkdir(parents=True, exist_ok=True)
    if (output / "ROUND_LOCK.json").exists():
        raise RuntimeError("Audit is immutable once search begins; use recorded audit")
    root = config["data"]["root"]
    if root is None:
        result = {"status": "BLOCKED", "reason": "Data V4 not found; set SYNAP_DATA_ROOT", "historical_test_exposure": True}
        write_json(output / "DATA_AUDIT.json", result)
        return result
    root = Path(root)
    manifest, annotations = root / "manifests/images.csv", root / "manifests/annotations.jsonl"
    result = validate_data_v4(root, manifest, annotations)
    frame = pd.read_csv(manifest, dtype=str, encoding="utf-8")
    required = ["image_uid", "patient_uid", "center_id", "image_path", "position_norm", "image_label_max", "split", "image_hash_v2"]
    if frame[required].isna().any().any():
        raise ValueError("Required manifest metadata is missing")
    if (frame.groupby("image_hash_v2")["split"].nunique() > 1).any():
        raise ValueError("Identical image content crosses native splits")
    if (frame.groupby("image_hash_v2")["patient_uid"].nunique() > 1).any():
        raise ValueError("Identical image content assigned to different patients")
    if not set(frame.position_norm).issubset(set(map(str, range(1, 7)))):
        raise ValueError("Unknown position labels")
    for value in frame.image_label_max.unique():
        FormalImageDataset._score_to_bin(value)
    rows = {row.image_uid: row for row in frame.itertuples(index=False)}
    grouped, shapes = {}, Counter()
    for line in annotations.read_text(encoding="utf-8").splitlines():
        ann = json.loads(line)
        uid = ann["image_uid"]
        if uid not in rows or ann["coordinate_frame"] != "roi_crop":
            raise ValueError("Orphan annotation or incorrect coordinate frame")
        label = float(ann["lesion_label_float"])
        FormalImageDataset._score_to_bin(str(label))
        x1, y1, x2, y2 = [float(ann[f"bbox_crop_norm_{k}"]) for k in ("x_min", "y_min", "x_max", "y_max")]
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            raise ValueError("Invalid normalized box geometry")
        grouped.setdefault(uid, []).append(ann)
        shapes[str(ann.get("shape_type_raw", "unspecified"))] += 1
    missing = mismatch = lower_boxes = zero = 0
    for uid, row in rows.items():
        values = grouped.get(uid, [])
        missing += not bool(values)
        if values:
            maximum = max(float(a["lesion_label_float"]) for a in values)
            mismatch += not math.isclose(maximum, float(row.image_label_max), abs_tol=1e-6)
            lower_boxes += sum(float(a["lesion_label_float"]) < maximum for a in values)
            zero += maximum == 0
    if mismatch:
        raise ValueError("image_label_max does not match annotation maximum")
    # Full deterministic content verification belongs here, never inside training.
    for index, row in enumerate(frame.itertuples(index=False), 1):
        path = safe_image_path(root, row.image_path, row.split)
        if sha256(path) != row.image_hash_v2:
            raise ValueError("Image content hash mismatch")
        if index % 10000 == 0:
            print(json.dumps({"audit_verified_images": index}), flush=True)
    dev = frame.loc[frame.split != "test", required].copy()
    train = inner_partition(dev.loc[dev.split == "train"], config["data"]["inner_seed"], config["data"]["inner_fraction"])
    dev = dev.merge(train[["image_uid", "inner_split"]], on="image_uid", how="left")
    dev["inner_split"] = dev.inner_split.fillna("native_val")
    dev["parent_image_uid"] = dev.image_uid
    dev["original_split"] = dev.split
    dev["recipe_version"] = config["data"]["recipe_version"]
    dev["source_annotation_sha256"] = dev.image_uid.map(lambda uid: digest(grouped.get(uid, [])))
    private = output / "development"
    private.mkdir(exist_ok=True)
    dev.to_csv(private / "images.csv", index=False, encoding="utf-8")
    for partition in ("inner_train", "inner_val", "native_train", "native_val"):
        subset = dev.loc[dev.inner_split == partition] if partition.startswith("inner") else dev.loc[dev.split == partition.removeprefix("native_")]
        with (private / f"{partition}.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
            for uid in subset.image_uid:
                for ann in grouped.get(uid, []):
                    # Strip all unrelated metadata, including patient-wide labels.
                    fields = ["image_uid", "coordinate_frame", "lesion_label_float"] + [f"bbox_crop_norm_{k}" for k in ("x_min", "y_min", "x_max", "y_max")]
                    handle.write(json.dumps({k: ann[k] for k in fields}) + "\n")
    gray = []
    # Pixel statistics only from inner train, no native-val or test fitting.
    for row in train.loc[train.inner_split == "inner_train"].head(128).itertuples(index=False):
        image = cv2.imread(str(root / row.image_path)).astype(float)
        gray.append(float(np.max(image, axis=2).mean() - np.min(image, axis=2).mean()))
    result.update(status="PASS", historical_test_exposure=True,
                  image_hashes_verified=len(frame), duplicate_cross_split_hashes=0,
                  position_mapping={str(i): i - 1 for i in range(1, 7)}, anatomical_names="not established; numeric codes retained",
                  development_position_counts=dev.groupby("split").position_norm.value_counts().unstack(fill_value=0).to_dict(orient="index"),
                  missing_annotations=missing, annotation_max_mismatches=mismatch, lower_severity_boxes=lower_boxes,
                  score_zero_images=zero, annotation_shape_types=dict(shapes),
                  contour_truth=False, annotation_completeness="unknown outside recorded boxes; missing is not negative",
                  inner_train_channel_spread_mean_128=float(np.mean(gray)),
                  inner_counts=train.inner_split.value_counts().to_dict(),
                  development_files={p.name: sha256(p) for p in sorted(private.iterdir()) if p.is_file()})
    write_json(output / "DATA_AUDIT.json", result)
    write_json(output / "ENVIRONMENT.json", environment())
    write_json(output / "SOURCE_BASELINE.json", source_fingerprint())
    return result
