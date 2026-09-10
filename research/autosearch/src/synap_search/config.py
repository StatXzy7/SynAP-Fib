from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import os
import yaml


@dataclass(frozen=True)
class ModelConfig:
    mechanism: str = "M1"
    decoder: str = "c4"
    width: int = 64
    stride: int = 8
    auxiliary_eta: float = 0.3
    injection_eta: float = 0.0
    fusion: str = "none"
    position_weight: float = 0.1
    lesion_weight: float = 0.1
    warmup: int = 0
    loss: str = "legacy"
    local_weight: float = 0.1

    def __post_init__(self):
        if self.mechanism not in {"A_legacy", "A_tuned", "E_reference", "M0", "M1", "M2", "M3", "M4", "G_slow"}:
            raise ValueError("Unknown mechanism")
        if self.decoder not in {"c4", "fpn"} or self.width not in {64, 128} or self.stride not in {4, 8}:
            raise ValueError("Invalid decoder")
        if self.auxiliary_eta not in {0, 0.1, 0.3, 1} or self.injection_eta not in {0, 0.1, 0.3, 1}:
            raise ValueError("Invalid independent gradient scale")
        if self.fusion not in {"none", "feature", "logit", "experts"}:
            raise ValueError("Invalid fusion")
        if self.mechanism in {"M1", "M2"} and self.fusion != "none":
            raise ValueError("M1/M2 do not inject predictions")
        if self.mechanism in {"M3", "M4"} and self.fusion == "none":
            raise ValueError("M3/M4 require fusion")
        if self.warmup not in {0, 10, 20} or self.loss not in {"legacy", "cdf"}:
            raise ValueError("Invalid objective recipe")
        if min(self.position_weight, self.lesion_weight, self.local_weight) < 0:
            raise ValueError("Negative loss weights")


@dataclass(frozen=True)
class TrainConfig:
    seed: int = 31001
    epochs: int = 120
    batch_size: int = 24
    workers: int = 0
    lr: float = 1e-4
    head_multiplier: float = 1
    weight_decay: float = 1e-4
    scheduler: str = "step"
    precision: str = "fp32"
    ema: float = 0.0
    pretrained: bool = True
    device: str = "cuda"

    def __post_init__(self):
        if self.epochs != 120 or self.batch_size < 1 or self.workers < 0:
            raise ValueError("Fixed 120 epoch horizon; positive batch and nonnegative workers required")
        if self.scheduler not in {"step", "cosine"} or self.precision not in {"fp32", "bf16", "fp16"}:
            raise ValueError("Invalid runtime recipe")
        if self.ema not in {0, 0.999} or self.lr <= 0 or self.weight_decay < 0 or self.head_multiplier <= 0:
            raise ValueError("Invalid optimizer recipe")


@dataclass(frozen=True)
class DataConfig:
    root: str | None = None
    output: str | None = None
    image_size: int = 512
    resize: str = "stretch"
    augmentation: str = "legacy"
    inner_seed: int = 31001
    inner_fraction: float = 0.2
    recipe_version: str = "v1"

    def __post_init__(self):
        if self.resize not in {"stretch", "letterbox"} or self.augmentation not in {"legacy", "conservative", "none"}:
            raise ValueError("Unsupported geometry/augmentation; no GT-based input crops")
        if self.image_size < 32 or self.image_size % 32 or not 0 < self.inner_fraction < 1:
            raise ValueError("Invalid image size or patient split fraction")


def load_config(path):
    path = Path(path).resolve()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    data = dict(raw["data"])
    root = os.environ.get("SYNAP_DATA_ROOT") or data.get("root")
    if not root:
        # Discover actual existing datasets relative to the checked-out config.
        candidates = [p / "data/processed/schisto_2024_clean_v4" for p in path.parents]
        root = next((str(p) for p in candidates if (p / "manifests/images.csv").is_file()), None)
    data["root"] = str(Path(root).resolve()) if root else None
    data["output"] = str(Path(os.environ.get("SYNAP_OUTPUT_ROOT") or data.get("output") or path.parent.parent / "outputs").resolve())
    raw["data"] = asdict(DataConfig(**data))
    raw["train"] = asdict(TrainConfig(**raw["train"]))
    if raw["search"]["seeds"] != [34001, 34002, 34003]:
        raise ValueError("Confirmation seeds are fixed")
    if [raw["search"][k] for k in ("baseline_trials", "mechanism_trials", "recipe_trials")] != [8, 24, 8]:
        raise ValueError("Changing the registered budget requires a new protocol round")
    if raw["constraints"] != {"position_macro_f1_tolerance": 0.0, "weak_box_iou_tolerance": 0.0, "aggregation": "mean_over_fixed_seeds"}:
        raise ValueError("Frozen constraints cannot be relaxed")
    return raw
