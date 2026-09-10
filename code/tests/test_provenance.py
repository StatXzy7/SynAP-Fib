from __future__ import annotations

import json

import pytest
import torch

from sfibai_b.provenance import (
    audit_initialization_records,
    model_initialization_record,
)


def _record(shared: str, position: str | None, lesion: str | None) -> dict:
    tensors = {
        "backbone.weight": {"sha256": shared},
        "grading_head.weight": {"sha256": shared},
    }
    if position is not None:
        tensors["position_head.weight"] = {"sha256": position}
    if lesion is not None:
        tensors["lesion_head.0.weight"] = {"sha256": lesion}
    return {"seed": 2026, "tensors": tensors}


def test_model_initialization_record_hashes_every_tensor() -> None:
    model = torch.nn.Sequential(torch.nn.Linear(2, 3), torch.nn.BatchNorm1d(3))
    record = model_initialization_record(model, seed=2026, arm="A")

    assert record["seed"] == 2026
    assert record["arm"] == "A"
    assert set(record["tensors"]) == set(model.state_dict())
    assert all(len(item["sha256"]) == 64 for item in record["tensors"].values())


def test_pairing_audit_requires_shared_and_branch_specific_initialization() -> None:
    records = {
        "A": _record("a" * 64, None, None),
        "E": _record("a" * 64, "c" * 64, "d" * 64),
        "G": _record("a" * 64, "c" * 64, "d" * 64),
    }

    audit = audit_initialization_records(records, seed=2026)
    assert audit["ok"] is True
    assert audit["comparisons"]["shared_all_arms"]["ok"] is True
    assert audit["comparisons"]["position_all_aux"]["ok"] is True
    assert audit["comparisons"]["lesion_all_aux"]["ok"] is True


def test_pairing_audit_rejects_one_mismatched_shared_tensor() -> None:
    records = {
        "A": _record("a" * 64, None, None),
        "E": _record("b" * 64, "c" * 64, "d" * 64),
        "G": _record("a" * 64, "c" * 64, "d" * 64),
    }
    with pytest.raises(ValueError, match="paired initialization"):
        audit_initialization_records(records, seed=2026)
