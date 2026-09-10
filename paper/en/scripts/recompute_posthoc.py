"""Post-hoc metric recomputation for the SynAP-Fib TMI manuscript.

Scope is deliberately narrow and frozen (see DECISIONS.md sections 3 and 5):

1. Validation pass -- recompute global image-level MAE, 4-class accuracy,
   +/-0.3 and +/-0.5 accuracy and severe-error rate from the frozen
   ``predictions_full.csv.gz`` bundles and compare them against the frozen
   ``metrics.json``.  Any mismatch is a hard failure that invalidates all
   downstream manuscript generation.
2. Stage-wise MAE for F0-F3 (Figure 3a).
3. Image-level 36-grade quadratic weighted kappa (Supplementary only).

No other derived quantity is produced here.  The script never writes to the
frozen experiment tree; it only reads from it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

# Grade boundaries are fixed by EVALUATION_POLICY.md: 0.5 / 1.5 / 2.5, with
# boundary values falling into the higher grade.
GRADE_BOUNDARIES = (0.5, 1.5, 2.5)
ARMS = ("A", "B", "C", "D", "E")
# 36-bin ordinal head: scores 0.0..3.5 in steps of 0.1.
N_BINS = 36
BIN_STEP = 0.1
# Tolerance for float64 aggregation differences against the frozen metrics.
TOL = 1e-6


def to_grade(score: np.ndarray) -> np.ndarray:
    """Map a continuous fibrosis score to the clinical 4-grade scale."""
    return np.digitize(score, GRADE_BOUNDARIES, right=False)


def to_bin(score: np.ndarray) -> np.ndarray:
    """Map a continuous fibrosis score to its 36-bin ordinal index.

    This rounds the continuous posterior expectation to the nearest bin.  It is
    deliberately *not* the stored posterior-argmax ``pred_bin`` field: the two
    disagree on 1,601 of 4,107 test images, and the manuscript reports the
    expectation (see FACTS.md F-DEF-SCORE), so the expectation is what is
    discretized here.  ``np.rint`` uses banker's rounding at exact half-bin
    values; no test prediction falls exactly on a half-bin boundary, so this has
    no effect on the frozen results.
    """
    return np.clip(np.rint(score / BIN_STEP), 0, N_BINS - 1).astype(int)


def load_arm(root: Path, arm: str) -> pd.DataFrame:
    path = root / "seed_2026" / arm / "best" / "test" / "predictions_full.csv.gz"
    if not path.exists():
        raise FileNotFoundError(f"missing frozen predictions for arm {arm}: {path}")
    df = pd.read_csv(path, usecols=["arm", "split", "image_uid", "true_score", "pred_score"])
    if not (df["arm"] == arm).all():
        raise ValueError(f"arm column mismatch in {path}")
    if not (df["split"] == "test").all():
        raise ValueError(f"split column mismatch in {path}")
    if df["image_uid"].duplicated().any():
        raise ValueError(f"duplicate image_uid in {path}")
    if not np.isfinite(df[["true_score", "pred_score"]].to_numpy()).all():
        raise ValueError(f"non-finite scores in {path}")
    return df


def load_frozen_metrics(root: Path, arm: str) -> dict:
    path = root / "seed_2026" / arm / "best" / "test" / "metrics.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)["image"]


def validate_arm(df: pd.DataFrame, frozen: dict, arm: str) -> list[dict]:
    """Recompute frozen scalars and compare. Returns one row per check."""
    true_score = df["true_score"].to_numpy(dtype=np.float64)
    pred_score = df["pred_score"].to_numpy(dtype=np.float64)
    err = np.abs(pred_score - true_score)
    true_grade = to_grade(true_score)
    pred_grade = to_grade(pred_score)
    grade_dist = np.abs(pred_grade - true_grade)

    recomputed = {
        "n": float(len(df)),
        "mae": float(err.mean()),
        "accuracy_within_0_3": float((err <= 0.3).mean()),
        "accuracy_within_0_5": float((err <= 0.5).mean()),
        "grade_accuracy": float((pred_grade == true_grade).mean()),
        # severe_error_rate is defined on the continuous score (|error| > 1.0),
        # not on grade distance.  Grade distance >= 2 is a separate quantity
        # that feeds the cor_severe_stage component of COR.
        "severe_error_rate": float((err > 1.0).mean()),
        "cor_severe_stage": float(0.10 * (grade_dist >= 2).mean()),
    }

    rows = []
    for key, value in recomputed.items():
        reference = float(frozen[key])
        delta = value - reference
        rows.append(
            {
                "arm": arm,
                "check": key,
                "recomputed": value,
                "frozen": reference,
                "abs_delta": abs(delta),
                "status": "PASS" if abs(delta) <= TOL else "FAIL",
            }
        )
    return rows


def stage_wise_mae(df: pd.DataFrame, arm: str) -> list[dict]:
    true_score = df["true_score"].to_numpy(dtype=np.float64)
    pred_score = df["pred_score"].to_numpy(dtype=np.float64)
    true_grade = to_grade(true_score)
    err = np.abs(pred_score - true_score)

    rows = []
    for grade in range(4):
        mask = true_grade == grade
        rows.append(
            {
                "arm": arm,
                "true_grade": f"F{grade}",
                "support": int(mask.sum()),
                "mae": float(err[mask].mean()) if mask.any() else float("nan"),
            }
        )
    return rows


def image_qwk(df: pd.DataFrame, arm: str) -> dict:
    """36-grade quadratic weighted kappa over the ordinal bin index."""
    true_bin = to_bin(df["true_score"].to_numpy(dtype=np.float64))
    pred_bin = to_bin(df["pred_score"].to_numpy(dtype=np.float64))
    qwk = cohen_kappa_score(
        true_bin, pred_bin, weights="quadratic", labels=list(range(N_BINS))
    )
    return {"arm": arm, "qwk_36grade_image": float(qwk)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experiment-root",
        type=Path,
        default=Path("research-private/experiments/SFibAI-B_AE_COR_v2"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent.parent / "tables")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    validation_rows: list[dict] = []
    stage_rows: list[dict] = []
    qwk_rows: list[dict] = []

    for arm in ARMS:
        df = load_arm(args.experiment_root, arm)
        frozen = load_frozen_metrics(args.experiment_root, arm)
        validation_rows.extend(validate_arm(df, frozen, arm))
        stage_rows.extend(stage_wise_mae(df, arm))
        qwk_rows.append(image_qwk(df, arm))

    validation = pd.DataFrame(validation_rows)
    validation.to_csv(args.out_dir / "posthoc_validation.csv", index=False)

    failures = validation[validation["status"] == "FAIL"]
    if not failures.empty:
        # Remove any stale outputs from an earlier successful run so that a
        # failed validation cannot leave usable-looking artifacts behind.
        for stale in ("stage_wise_mae.csv", "image_qwk.csv"):
            (args.out_dir / stale).unlink(missing_ok=True)
        print("HARD FAIL: recomputed values disagree with frozen metrics.", file=sys.stderr)
        print(failures.to_string(index=False), file=sys.stderr)
        print(
            "\nDownstream manuscript generation is invalidated until resolved "
            "(DECISIONS.md, failure protocol 3).",
            file=sys.stderr,
        )
        return 1

    pd.DataFrame(stage_rows).to_csv(args.out_dir / "stage_wise_mae.csv", index=False)
    pd.DataFrame(qwk_rows).to_csv(args.out_dir / "image_qwk.csv", index=False)

    print(f"Validation: {len(validation)} checks, all PASS (tol={TOL:g}).")
    print("\nStage-wise MAE:")
    print(pd.DataFrame(stage_rows).pivot(index="arm", columns="true_grade", values="mae").to_string())
    print("\nSupport per stage:")
    print(pd.DataFrame(stage_rows).pivot(index="arm", columns="true_grade", values="support").to_string())
    print("\n36-grade image-level QWK:")
    print(pd.DataFrame(qwk_rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
