from __future__ import annotations

import pytest

from sfibai_b.protocol import SEEDS
from sfibai_b.ranking import rank_test_results


def _completion(value: float) -> dict:
    return {
        "best_epoch": 40,
        "best_checkpoint_sha256": "a" * 64,
        "last_checkpoint_sha256": "b" * 64,
        "best_test": {
            "r_final": value,
            "image": {"cor": value + 0.01, "mae": value + 0.02},
            "patient_max": {"cor": value + 0.03},
            "patient_median": {"cor": value + 0.04},
            "center_balanced_patient_max": {"cor": value + 0.05},
        },
        "last_test": {
            "r_final": value + 0.02,
            "image": {"cor": value + 0.03, "mae": value + 0.04},
            "patient_max": {"cor": value + 0.05},
            "patient_median": {"cor": value + 0.06},
            "center_balanced_patient_max": {"cor": value + 0.07},
        },
    }


def test_final_ranking_uses_single_seed_best_test_r_final() -> None:
    completions = {}
    for arm, base in zip("AEG", [0.30, 0.24, 0.22]):
        completions[(arm, SEEDS[0])] = _completion(base)

    report = rank_test_results(completions)

    assert [row["arm"] for row in report["ranking"]] == ["G", "E", "A"]
    assert report["single_seed"] == SEEDS[0]
    e = next(row for row in report["ranking"] if row["arm"] == "E")
    assert e["candidate_minus_a"] == pytest.approx(-0.06)
    assert e["last_test_r_final"] == pytest.approx(0.26)
    assert set(e["checkpoint_sha256"]) == {"best", "last"}
    assert {item["name"] for item in report["contrasts"]} == {
        "E-A",
        "G-A",
        "G-E",
    }
