"""Render Figure 5 candidate montages for supervisor selection.

For each candidate image: original ROI, lesion attention overlay, and a panel
with true/predicted score and position. Output is a review sheet PNG per
group (F0-F3, failure), not the final figure. No numbers are invented: true
and predicted scores come from the frozen predictions; the overlay is the
frozen 32x32 attention upsampled to the image size.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

REPO = Path(__file__).resolve().parents[4]
R = REPO / 'research-private' / 'experiments' / 'SFibAI-B_AE_COR_v2'
IMG_ROOT = REPO / 'data' / 'processed' / 'schisto_2024_clean_v4'

mpl.rcParams.update({'font.size': 7, 'pdf.fonttype': 42})

def main() -> None:
    cands = json.loads(Path('tables/fig5_candidates.json').read_text(encoding='utf-8'))
    att = np.load(R / 'seed_2026/E/best/test/lesion_attention_float16.npz')
    amap = {u: i for i, u in enumerate(list(att['image_uid']))}
    att_arr = att['attention'].astype(np.float32)

    for grp, rows in cands.items():
        n = len(rows)
        fig, axes = plt.subplots(n, 2, figsize=(4.2, 1.9 * n))
        if n == 1:
            axes = axes.reshape(1, -1)
        for i, r in enumerate(rows):
            path = IMG_ROOT / 'test' / r['center'] / (r['image_uid'] + '_roi.jpg')
            img = np.asarray(Image.open(path).convert('L'))
            a = att_arr[amap[r['image_uid']]]
            # upsample 32x32 -> image size by PIL bilinear
            a_up = np.asarray(
                Image.fromarray((a * 255).astype(np.uint8))
                .resize((img.shape[1], img.shape[0]), Image.BILINEAR)
            ) / 255.0

            axes[i, 0].imshow(img, cmap='gray')
            axes[i, 0].set_title(f"{r['image_uid']}\ntrue {r['true_score']:.1f} / pred {r['pred_score']:.2f}",
                                  loc='left', fontsize=6)
            axes[i, 0].axis('off')

            axes[i, 1].imshow(img, cmap='gray')
            axes[i, 1].imshow(a_up, cmap='inferno', alpha=0.45)
            axes[i, 1].set_title(f"attention  pos {r['position_true']}/{r['position_pred']}",
                                  loc='left', fontsize=6)
            axes[i, 1].axis('off')

        fig.suptitle(f'Fig 5 candidates: {grp} (review only)', fontsize=8)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        out = Path('figures') / f'fig5_review_{grp}.png'
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f'wrote {out} ({n} cases)')


if __name__ == '__main__':
    main()
