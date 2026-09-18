"""Supplementary figures S1-S3.

S1: per-center descriptive patient-max COR, arms A-E, patient counts on the
    x axis. Caption constraints (DECISIONS.md 4.2): title must not contain
    "robustness" or "generalization"; caption states all test centers were
    represented in the training split.
S2: error distribution -- histogram of per-image absolute error, arms A and E
    (source: frozen errors.csv, FACTS F-SUPP-S2).
S3: training and checkpoint-selection trajectories -- per-epoch validation
    R_final, all five arms, selected epoch marked (source: frozen
    seed_2026/<arm>/val_epochs/epoch_NNN/metrics.json, FACTS F-SUPP-S3).
    No smoothing.

All numbers come from the frozen experiment tree (read-only).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
EXP = Path(r"D:\PhD\liver-Fibrosis-B\research-private\experiments\SFibAI-B_AE_COR_v2")
PACK = EXP / "paper_plot_packs" / "seed_2026"
SEED = EXP / "seed_2026"

ARMS = ("A", "B", "C", "D", "E")
ARM_COLORS = {"A": "#8c8c8c", "B": "#c0c0c0", "C": "#5b9bd5", "D": "#ed9b40", "E": "#1f4e79"}
# FACTS.md F-RFINAL-* best epochs
BEST_EPOCH = {"A": 81, "B": 39, "C": 50, "D": 47, "E": 103}

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


def make_s1() -> None:
    centers = ("center_05", "center_07", "center_15", "center_17")
    patients = (2, 115, 93, 30)
    cor = {}
    for arm in ARMS:
        df = pd.read_csv(PACK / arm / "best_test" / "center.csv")
        df = df.set_index("center_id")
        cor[arm] = [float(df.loc[c, "cor"]) for c in centers]

    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    width = 0.8 / len(ARMS)
    positions = np.arange(len(centers))
    for i, arm in enumerate(ARMS):
        ax.bar(positions + (i - (len(ARMS) - 1) / 2) * width, cor[arm], width,
               label=f"Arm {arm}", color=ARM_COLORS[arm], edgecolor="black", linewidth=0.4)
    ax.set_xticks(positions)
    ax.set_xticklabels(f"{c}\n(n={n})" for c, n in zip(centers, patients))
    ax.set_xlabel("Test center (patients)")
    ax.set_ylabel("Patient-max COR")
    ax.set_title("Per-center descriptive performance", loc="left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(frameon=False, ncol=5, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout()
    fig.savefig(HERE / "supp_fig_s1.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote supp_fig_s1.pdf")


def make_s2() -> None:
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    bins = np.linspace(0, 3.5, 36)
    for arm in ("A", "E"):
        df = pd.read_csv(PACK / arm / "best_test" / "errors.csv")
        ax.hist(df["absolute_error"], bins=bins, histtype="step", linewidth=1.0,
                label="Baseline (A)" if arm == "A" else "SynAP-Fib (E)",
                color=ARM_COLORS[arm])
    ax.set_xlabel("Per-image absolute error")
    ax.set_ylabel("Images")
    ax.set_xlim(0, 3.5)
    ax.set_title("Distribution of per-image absolute error", loc="left")
    ax.grid(linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(HERE / "supp_fig_s2.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote supp_fig_s2.pdf")


def make_s3() -> None:
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    for arm in ARMS:
        epochs, values = [], []
        for ep in range(1, 121):
            mfile = SEED / arm / "val_epochs" / f"epoch_{ep:03d}" / "metrics.json"
            with mfile.open(encoding="utf-8") as fh:
                epochs.append(ep)
                values.append(json.load(fh)["r_final"])
        line, = ax.plot(epochs, values, linewidth=0.7, color=ARM_COLORS[arm], label=f"Arm {arm}")
        best = BEST_EPOCH[arm]
        best_val = values[BEST_EPOCH[arm] - 1]
        ax.plot([best], [best_val], marker="o", markersize=3.5, color=line.get_color())
    ax.axvspan(1, 20, color="#f2f2f2", zorder=0)
    ax.text(10.5, ax.get_ylim()[1] * 0.985, "burn-in", ha="center", va="top",
            fontsize=6.5, color="#808080")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Validation $R_{\\mathrm{final}}$")
    ax.set_title("Training and checkpoint-selection trajectories", loc="left")
    ax.set_xlim(1, 120)
    ax.grid(linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=5, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(HERE / "supp_fig_s3.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote supp_fig_s3.pdf")


if __name__ == "__main__":
    make_s1()
    make_s2()
    make_s3()
