"""Figure 3 -- Stage-wise performance of the baseline and SynAP-Fib.

Two panels, arms A and E only:
  (a) stage-wise MAE across F0-F3
  (b) stage-wise recall across F0-F3

Constraints (DECISIONS.md sections 3.1 and 4.2):
  - Title is "Stage-wise performance", never "improvement".
  - No delta annotations, no additive reference lines.
  - Per-stage support belongs in the caption, not on the bars.

MAE is loaded from the validated post-hoc table.  Recall is transcribed from
FACTS.md (F-STAGEREC-A / F-STAGEREC-E), which in turn reads the frozen
metrics.json field ``grade_f<k>_recall``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
TABLES = HERE.parent / "tables"

STAGES = ("F0", "F1", "F2", "F3")

# FACTS.md F-STAGEREC-A / F-STAGEREC-E, expressed as percentages.
RECALL = {
    "A": (80.18, 49.50, 63.63, 73.27),
    "E": (81.14, 50.50, 63.63, 72.10),
}

# FACTS.md F-TEST-GRADE-DIST -- identical across arms.
SUPPORT = {"F0": 1140, "F1": 1006, "F2": 1108, "F3": 853}

LABELS = {"A": "Baseline (A)", "E": "SynAP-Fib (E)"}
COLORS = {"A": "#8c8c8c", "E": "#1f4e79"}

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 8.5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.6,
        "pdf.fonttype": 42,
    }
)


def load_stage_mae() -> dict[str, tuple[float, ...]]:
    df = pd.read_csv(TABLES / "stage_wise_mae.csv")
    out = {}
    for arm in ("A", "E"):
        sub = df[df["arm"] == arm].set_index("true_grade")
        out[arm] = tuple(float(sub.loc[stage, "mae"]) for stage in STAGES)
    return out


def grouped_bars(ax, values: dict[str, tuple[float, ...]], ylabel: str, title: str) -> None:
    width = 0.36
    positions = range(len(STAGES))
    for offset, arm in ((-width / 2, "A"), (width / 2, "E")):
        ax.bar(
            [p + offset for p in positions],
            values[arm],
            width,
            label=LABELS[arm],
            color=COLORS[arm],
            edgecolor="black",
            linewidth=0.4,
        )
    ax.set_xticks(list(positions))
    ax.set_xticklabels(STAGES)
    ax.set_xlabel("True fibrosis stage")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def main() -> None:
    mae = load_stage_mae()

    # IEEE double-column width is about 7.16 in.
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.6))

    grouped_bars(axes[0], mae, "Mean absolute error", "(a) Stage-wise MAE")
    axes[0].set_ylim(0, max(max(v) for v in mae.values()) * 1.18)

    grouped_bars(axes[1], RECALL, "Recall (%)", "(b) Stage-wise recall")
    axes[1].set_ylim(0, 100)

    axes[1].legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout()

    out = HERE / "fig3_stage_wise.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    support = ", ".join(f"{s} $n={SUPPORT[s]}$" for s in STAGES)
    caption = (
        "Fig. 3. Stage-wise performance of the baseline (A) and SynAP-Fib (E) on the "
        "patient-held-out test set (seed 2026, validation-selected checkpoints). "
        "(a) Stage-wise mean absolute error, recomputed post hoc from the frozen "
        "per-image predictions. (b) Stage-wise recall of the four clinical grades. "
        f"Per-stage image support: {support}. Lower is better in (a); higher is better in (b)."
    )
    (HERE / "fig3_caption.txt").write_text(caption + "\n", encoding="utf-8")

    print(f"wrote {out}")
    print(f"wrote {HERE / 'fig3_caption.txt'}")


if __name__ == "__main__":
    main()
