"""Figure 1 -- SynAP-Fib architecture (publication rendering).

Renders the same diagram as figures/fig1_architecture.drawio (the editable
source). Mechanisms depicted (DECISIONS.md 4.2): backbone -> position/lesion
branches -> gated residual injection -> grading head, bidirectional detach
marked. Only mechanisms that exist in the frozen implementation
(model.py: SFibAIModel) are drawn.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "pdf.fonttype": 42,
    }
)

BLUE = "#1f4e79"
BLUE_FILL = "#dce6f1"
ORANGE = "#ed9b40"
ORANGE_FILL = "#fdf2e3"
RED = "#c0504d"
RED_FILL = "#fde9e8"
GRAY_FILL = "#f5f5f5"
GOLD = "#d6b656"
GOLD_FILL = "#fff2cc"


def box(ax, x, y, w, h, lines, edge, fill, fontsize=8, dashed=False):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                       facecolor=fill, edgecolor=edge, linewidth=0.9,
                       linestyle="--" if dashed else "-")
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, "\n".join(lines), ha="center", va="center",
            fontsize=fontsize, linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, color, style="-|>", dashed=False, lw=1.2):
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=10,
                        color=color, linewidth=lw,
                        linestyle="--" if dashed else "-", zorder=1,
                        shrinkA=0, shrinkB=0)
    ax.add_patch(a)


def main() -> None:
    fig, ax = plt.subplots(figsize=(7.16, 3.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 47)
    ax.axis("off")

    # Input -> backbone -> feature
    box(ax, 1, 19, 12, 9, ["Input image", "3 × 512 × 512", "ImageNet norm."], "#666666", GRAY_FILL)
    box(ax, 16, 19, 13, 9, ["ResNet-50", "backbone", "(IMAGENET1K_V2)"], BLUE, BLUE_FILL)
    box(ax, 33, 21.5, 8, 4, ["feature"], BLUE, "#e8eef7", fontsize=7)
    arrow(ax, 13, 23.5, 16, 23.5, BLUE)
    arrow(ax, 29, 23.5, 33, 23.5, BLUE)

    # Position branch (top)
    box(ax, 45, 35, 14, 8.5, ["Position branch", "6-class head"], ORANGE, ORANGE_FILL)
    box(ax, 63, 35, 14, 8.5, ["Position residual", "(MLP → feat dim)"], ORANGE, ORANGE_FILL)
    box(ax, 81, 35.5, 10, 7.5, ["gate", "≤ 0.5"], ORANGE, ORANGE_FILL, fontsize=7)
    arrow(ax, 41, 23.5, 41, 39.2, ORANGE)
    arrow(ax, 41, 39.2, 45, 39.2, ORANGE)
    arrow(ax, 59, 39.2, 63, 39.2, ORANGE)
    arrow(ax, 77, 39.2, 81, 39.2, ORANGE)
    # gated residual into grading head input (dashed)
    arrow(ax, 86, 35.5, 86, 30.5, ORANGE, dashed=True)
    arrow(ax, 86, 30.5, 74, 30.5, ORANGE, dashed=True)
    arrow(ax, 74, 30.5, 74, 28, ORANGE, dashed=True)
    ax.text(86.7, 33.0, "residual", fontsize=6.5, color=ORANGE, ha="left", va="center")

    # Lesion branch (bottom)
    box(ax, 45, 3, 14, 8.5, ["Lesion branch", "weak-box attention"], RED, RED_FILL)
    box(ax, 63, 3, 14, 8.5, ["Lesion residual", "(weighted feat)"], RED, RED_FILL)
    box(ax, 81, 3.5, 10, 7.5, ["gate", "≤ 0.5"], RED, RED_FILL, fontsize=7)
    arrow(ax, 41, 23.5, 41, 7.2, RED)
    arrow(ax, 41, 7.2, 45, 7.2, RED)
    arrow(ax, 59, 7.2, 63, 7.2, RED)
    arrow(ax, 77, 7.2, 81, 7.2, RED)
    arrow(ax, 86, 11, 86, 16, RED, dashed=True)
    arrow(ax, 86, 16, 74, 16, RED, dashed=True)
    arrow(ax, 74, 16, 74, 19, RED, dashed=True)
    ax.text(86.7, 12.8, "residual", fontsize=6.5, color=RED, ha="left", va="center")

    # Grading head chain (middle)
    box(ax, 63, 19, 14, 9, ["Grading head", "Linear(36)", "+ LayerNorm"], BLUE, BLUE_FILL)
    arrow(ax, 41, 23.5, 63, 23.5, BLUE)
    box(ax, 81, 19, 10, 9, ["36-bin", "posterior", "(softmax)"], BLUE, BLUE_FILL, fontsize=7)
    arrow(ax, 77, 23.5, 81, 23.5, BLUE)
    box(ax, 93, 19, 6.5, 9, ["ŷ =", "E[p]"], BLUE, BLUE_FILL, fontsize=7)
    arrow(ax, 91, 23.5, 93, 23.5, BLUE)

    # Detach markers on both injection paths (drawn as small barred circles)
    for (x, y) in ((74.9, 29.6), (74.9, 17.6)):
        circ = plt.Circle((x, y), 0.55, facecolor="white", edgecolor=RED, linewidth=0.8)
        ax.add_patch(circ)
        ax.plot([x - 0.3, x + 0.3], [y - 0.3, y + 0.3], color=RED, linewidth=0.9)
    ax.text(74.3, 31.8, "bidirectional detach", fontsize=6.5, color=RED, ha="right")
    ax.text(74.3, 15.0, "bidirectional detach", fontsize=6.5, color=RED, ha="right")

    # Training-only labels (dashed gold notes)
    box(ax, 45, 43.5, 14, 3.2, ["Position GT (train only)"], GOLD, GOLD_FILL, fontsize=6.5, dashed=True)
    arrow(ax, 52, 43.5, 52, 41, GOLD, style="-|>", dashed=True, lw=0.8)
    box(ax, 45, 0.0, 14, 3.2, ["Weak boxes (F1–F3 only)"], GOLD, GOLD_FILL, fontsize=6.5, dashed=True)
    arrow(ax, 52, 3.2, 52, 3.0, GOLD, style="-|>", dashed=True, lw=0.8)
    box(ax, 93, 32, 6.5, 3.2, ["Grade (all)"], GOLD, GOLD_FILL, fontsize=6.5, dashed=True)
    arrow(ax, 96.2, 32, 86, 28.5, GOLD, style="-|>", dashed=True, lw=0.8)

    # Legend for edge styles
    ax.plot([1, 3.2], [44.2, 44.2], color=BLUE, lw=1.2)
    ax.text(3.8, 44.2, "forward path", fontsize=6.5, va="center")
    ax.plot([16, 18.2], [44.2, 44.2], color=ORANGE, lw=1.2, ls="--")
    ax.text(18.8, 44.2, "gated residual (detached)", fontsize=6.5, va="center")

    fig.savefig(HERE / "fig1_architecture.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote fig1_architecture.pdf")


if __name__ == "__main__":
    main()
