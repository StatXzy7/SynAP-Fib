"""Figure 2 -- Cohort flow and label/position distributions across splits.

Three panels:
  (a) cohort flow: total -> train / validation / test (images / patients / centers)
  (b) patient-level grade distribution per split
  (c) image-level position distribution per split

All values from FACTS.md:
  F-COHORT-*, F-DIST-PAT-*, F-TRAIN/VAL/TEST-POSITION-DIST, F-SPLIT-PATIENT-OVERLAP,
  F-SPLIT-CENTER-SHARED, F-SPLIT-TEST-CENTERS.

Constraints (DECISIONS.md sections 3.4, 5.1):
  - No design-intent claims for the test composition (observed counts only).
  - Center sharing disclosed as structural fact.
  - No "external-center" vocabulary.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent

# FACTS.md F-COHORT-* (images, patients, centers)
TOTAL = (108_709, 6_373, 35)
SPLITS = {
    "Train": (83_722, 4_906, 35),
    "Validation": (20_880, 1_227, 33),
    "Test": (4_107, 240, 4),
}

# FACTS.md F-DIST-PAT-* (patient-level grade counts)
PAT_GRADES = {
    "Train": (854, 1_161, 1_977, 914),
    "Validation": (213, 291, 495, 228),
    "Test": (60, 60, 60, 60),
}

# FACTS.md F-TRAIN/VAL/TEST-POSITION-DIST (image counts, p1..p6)
POSITIONS = {
    "Train": (14_137, 14_092, 14_121, 14_047, 13_960, 13_365),
    "Validation": (3_515, 3_524, 3_556, 3_521, 3_478, 3_286),
    "Test": (694, 699, 689, 671, 682, 672),
}

STAGES = ("F0", "F1", "F2", "F3")
SPLIT_COLORS = {"Train": "#1f4e79", "Validation": "#5b9bd5", "Test": "#a6a6a6"}

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


def draw_flow(ax: plt.Axes) -> None:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("(a) Cohort and split", loc="left")

    def box(x, y, w, h, title, lines, fc):
        ax.add_patch(
            plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor="black", linewidth=0.7)
        )
        ax.text(x + w / 2, y + h - 0.55, title, ha="center", va="top", fontsize=8, fontweight="bold")
        for i, line in enumerate(lines):
            ax.text(x + w / 2, y + h - 1.5 - i * 0.78, line, ha="center", va="top", fontsize=7.5)

    def arrow(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", linewidth=0.8, color="black"))

    box(2.8, 7.2, 4.4, 2.2, "Study cohort",
        [f"{TOTAL[0]:,} images", f"{TOTAL[1]:,} patients", f"{TOTAL[2]} centers"],
        "#dce6f1")
    xs = {"Train": 0.3, "Validation": 3.55, "Test": 6.8}
    for name, (img, pat, cen) in SPLITS.items():
        x = xs[name]
        box(x, 3.0, 2.9, 2.4, name,
            [f"{img:,} images", f"{pat:,} patients", f"{cen} centers"], "#f2f2f2")
        arrow(5.0, 7.2, x + 1.45, 5.4)

    ax.text(5.0, 2.3,
            "Patient-level partition, zero patient overlap.\n"
            "All four test centers also appear in the training split.",
            ha="center", va="top", fontsize=7.5, style="italic")


def grouped_bars(ax, values: dict, categories: tuple[str, ...], xlabel: str,
                 title: str, ylabel: str) -> None:
    n = len(values)
    width = 0.8 / n
    positions = np.arange(len(categories))
    for i, (name, vals) in enumerate(values.items()):
        ax.bar(positions + (i - (n - 1) / 2) * width, vals, width,
               label=name, color=SPLIT_COLORS[name], edgecolor="black", linewidth=0.4)
    ax.set_xticks(positions)
    ax.set_xticklabels(categories)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def main() -> None:
    fig = plt.figure(figsize=(7.16, 4.6))
    gs = fig.add_gridspec(2, 2, height_ratios=(1.15, 1.0), hspace=0.42, wspace=0.28)

    ax_a = fig.add_subplot(gs[0, :])
    draw_flow(ax_a)

    ax_b = fig.add_subplot(gs[1, 0])
    grouped_bars(ax_b, PAT_GRADES, STAGES, "Patient-level fibrosis grade",
                 "(b) Grade distribution (patients)", "Patients")
    # legend above the low F0 bars (upper left) instead of over the tall F2 bars
    ax_b.legend(frameon=False, loc="upper left", fontsize=7)

    ax_c = fig.add_subplot(gs[1, 1])
    grouped_bars(ax_c, POSITIONS, tuple(f"p{i}" for i in range(1, 7)),
                 "Normalized anatomical position",
                 "(c) Position distribution (images)", "Images")

    out = HERE / "fig2_cohort.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
