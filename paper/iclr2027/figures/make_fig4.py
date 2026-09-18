"""Figure 4 -- Confusion matrices and reliability diagrams, arms A and E.

Four panels:
  (a) four-grade confusion matrix, A
  (b) four-grade confusion matrix, E
  (c) reliability diagram, A
  (d) reliability diagram, E

Data sources (FACTS.md 8.6, F-CONF-A / F-CONF-E / F-CAL-SOURCE):
  confusion.csv and calibration.csv from the frozen paper_plot_packs
  (read-only). Confusion row sums reproduce F-TEST-GRADE-DIST.

Constraints: descriptive display only; no derived deltas between arms.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PACK = Path(
    r"D:\PhD\liver-Fibrosis-B\research-private\experiments"
    r"\SFibAI-B_AE_COR_v2\paper_plot_packs\seed_2026"
)

STAGES = ("F0", "F1", "F2", "F3")
GRADE_COLORS = {0: "#8c8c8c", 1: "#5b9bd5", 2: "#ed9b40", 3: "#c0504d"}
ARM_TITLES = {"A": "Baseline (A)", "E": "SynAP-Fib (E)"}

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 8.5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7.5,
        "axes.linewidth": 0.6,
        "pdf.fonttype": 42,
    }
)


def confusion_panel(ax: plt.Axes, arm: str) -> None:
    df = pd.read_csv(PACK / arm / "best_test" / "confusion.csv")
    mat = np.zeros((4, 4), dtype=int)
    for _, row in df.iterrows():
        mat[int(row.true_grade), int(row.pred_grade)] = int(row["count"])
    row_frac = mat / mat.sum(axis=1, keepdims=True)

    im = ax.imshow(row_frac, cmap="Blues", vmin=0, vmax=1)
    for i in range(4):
        for j in range(4):
            frac = row_frac[i, j]
            color = "white" if frac > 0.5 else "black"
            ax.text(j, i, f"{mat[i, j]}\n({frac * 100:.1f}%)",
                    ha="center", va="center", fontsize=7, color=color)
    ax.set_xticks(range(4))
    ax.set_xticklabels(STAGES)
    ax.set_yticks(range(4))
    ax.set_yticklabels(STAGES)
    ax.set_xlabel("Predicted grade")
    ax.set_ylabel("True grade")
    ax.set_title(f"({chr(ord('a') + (arm == 'E'))}) Confusion, {ARM_TITLES[arm]}", loc="left")
    return im


def reliability_panel(ax: plt.Axes, arm: str) -> None:
    df = pd.read_csv(PACK / arm / "best_test" / "calibration.csv")
    ax.plot([0, 1], [0, 1], color="black", linewidth=0.7, linestyle="--", label="Perfect calibration")
    for grade, sub in df.groupby("grade"):
        sub = sub.sort_values("mean_probability")
        ax.plot(sub["mean_probability"], sub["observed_frequency"],
                marker="o", markersize=2.5, linewidth=0.8,
                color=GRADE_COLORS[int(grade)], label=f"Grade {STAGES[int(grade)]}")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Observed frequency")
    ax.set_title(f"({chr(ord('c') + (arm == 'E'))}) Reliability, {ARM_TITLES[arm]}", loc="left")
    ax.grid(linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left", fontsize=6.5, ncol=1)


def main() -> None:
    fig, axes = plt.subplots(1, 4, figsize=(7.16, 2.2))
    for ax, arm in zip(axes[:2], ("A", "E")):
        confusion_panel(ax, arm)
    for ax, arm in zip(axes[2:], ("A", "E")):
        reliability_panel(ax, arm)
    fig.tight_layout(w_pad=1.4)
    out = HERE / "fig4_confusion_calibration.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
