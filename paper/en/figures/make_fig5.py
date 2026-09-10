"""Figure 5 (PDF Figure 4) -- Qualitative cases for SynAP-Fib (arm E, best test).

Supervisor-selected cases (node B, 2026-09-05; F0-F2 from AskUserQuestion,
F3 and failure delegated):
  F0      img_center_17_2023157028_3_2  (true 0.2,  pred 0.21, pos 3/4)
  F1      img_center_07_2023080032_5_1  (true 1.4,  pred 1.64, pos 5/5)
  F2      img_center_07_2023080017_1_2  (true 2.2,  pred 1.87, pos 1/1)
  F3      img_center_07_2023080033_3_1  (true 3.2,  pred 2.98, pos 3/2)
  failure img_center_07_2023080131_4_3  (true 2.8,  pred 0.46, pos 4/4)

Each row, left to right:
  (1) ROI image with the expert-annotated lesion boxes (green);
  (2) the full lesion attention heatmap (complete [0, 1] range, including
      values below the 0.5 binarization threshold);
  (3) overlay of the image with the thresholded attention (attention >= 0.5,
      the binarization threshold used for weak-box agreement) plus the expert
      boxes for direct comparison.
Annotations: true score, predicted score, position (true/predicted). No
patient identifiers are printed on the figure.

Sources (read-only): frozen paper_plot_packs predictions and lesion attention
for arm E best test; the dataset manifest annotations.jsonl for expert boxes
and images.csv for original images.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
V4 = ROOT / 'data' / 'processed' / 'schisto_2024_clean_v4'
PACK = ROOT / 'research-private' / 'experiments' / 'SFibAI-B_AE_COR_v2' / 'seed_2026' / 'E' / 'best' / 'test'

CASES = [
    ('F0',      'img_center_17_2023157028_3_2'),
    ('F1',      'img_center_07_2023080032_5_1'),
    ('F2',      'img_center_07_2023080017_1_2'),
    ('F3',      'img_center_07_2023080033_3_1'),
    ('Failure', 'img_center_07_2023080131_4_3'),
]

ATTENTION_THRESHOLD = 0.5   # binarization threshold used for weak-box agreement
BOX_COLOR = '#00e676'

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "pdf.fonttype": 42,
    }
)


def _expert_boxes(uid: str) -> list[tuple[float, float, float, float]]:
    """Expert-annotated boxes for one image, in the ROI-crop frame.

    Returns (x_min, y_min, x_max, y_max) tuples normalized to the ROI crop.
    """
    boxes = []
    with (V4 / 'manifests' / 'annotations.jsonl').open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record['image_uid'] != uid:
                continue
            boxes.append((
                float(record['bbox_crop_norm_x_min']),
                float(record['bbox_crop_norm_y_min']),
                float(record['bbox_crop_norm_x_max']),
                float(record['bbox_crop_norm_y_max']),
            ))
    return boxes


def _draw_boxes(ax: plt.Axes, boxes, img_shape) -> None:
    h, w = img_shape
    for (x0, y0, x1, y1) in boxes:
        ax.add_patch(Rectangle(
            (x0 * w, y0 * h), (x1 - x0) * w, (y1 - y0) * h,
            fill=False, edgecolor=BOX_COLOR, linewidth=1.4))


def main() -> None:
    df = pd.read_csv(
        PACK / 'predictions_full.csv.gz',
        usecols=['image_uid', 'true_score', 'pred_score',
                 'position_true', 'position_pred'])
    df = df.set_index('image_uid')

    att = np.load(PACK / 'lesion_attention_float16.npz')
    amap = {u: i for i, u in enumerate(list(att['image_uid']))}
    attention = att['attention']          # (N, 1, 32, 32) float16

    n = len(CASES)
    fig, axes = plt.subplots(
        n, 3, figsize=(7.16, 2.15 * n),
        gridspec_kw={'wspace': 0.06, 'hspace': 0.28})

    for r, (label, uid) in enumerate(CASES):
        row = df.loc[uid]
        img = np.asarray(Image.open(_image_path(uid)).convert('L'),
                         dtype=np.float32) / 255.0

        a = attention[amap[uid]].astype(np.float32)
        a = a.reshape(32, 32)
        heat = np.array(Image.fromarray(a).resize(
            (img.shape[1], img.shape[0]), resample=Image.BILINEAR))
        heat_masked = np.ma.masked_less(heat, ATTENTION_THRESHOLD)
        boxes = _expert_boxes(uid)

        for c, ax in enumerate(axes[r]):
            ax.axis('off')
            if c == 0:
                ax.imshow(img, cmap='gray')
                _draw_boxes(ax, boxes, img.shape)
                title = 'ROI + expert boxes'
            elif c == 1:
                im = ax.imshow(heat, cmap='inferno', vmin=0, vmax=1)
                title = 'Lesion attention (full)'
            else:
                ax.imshow(img, cmap='gray')
                ax.imshow(heat_masked, cmap='inferno', alpha=0.55,
                          vmin=0, vmax=1)
                _draw_boxes(ax, boxes, img.shape)
                title = f'Overlay (attention $\\geq$ {ATTENTION_THRESHOLD:.1f})'
            if r == 0:
                ax.set_title(title, fontsize=8, pad=4)
            if c == 0:
                pos_txt = (f"{row.position_true:.0f}/"
                           f"{row.position_pred:.0f}")
                ax.text(
                    0.0, -0.10,
                    f"{label}: true {row.true_score:.1f}, "
                    f"pred {row.pred_score:.2f}, pos {pos_txt}",
                    transform=ax.transAxes, fontsize=7.5, va='top',
                    ha='left')

        # one shared colorbar, attached to the overlay column of the last row
        if r == n - 1:
            cax = fig.add_axes([
                axes[r, 2].get_position().x1 + 0.005,
                axes[r, 2].get_position().y0,
                0.012,
                axes[r, 2].get_position().height * n * 0.92])
            fig.colorbar(im, cax=cax)
            cax.tick_params(labelsize=6.5)

    out = HERE / 'fig5_qualitative.pdf'
    fig.savefig(out, bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'wrote {out}')


def _image_path(uid: str) -> Path:
    m = pd.read_csv(V4 / 'manifests' / 'images.csv',
                    usecols=['image_uid', 'image_path'])
    rel = m.loc[m.image_uid == uid, 'image_path'].iloc[0]
    return V4 / rel


if __name__ == '__main__':
    main()
