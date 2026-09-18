# FACTS.md — SynAP-Fib TMI manuscript

**Single source of truth for every quantitative statement in the manuscript.**

Governing rules (see `DECISIONS.md` §5):

1. Any quantitative statement not present in this file is **forbidden**.
2. Writing agents **must not compute any number themselves** — not even a subtraction of two
   values listed here.
3. If a needed value is missing, stop and request its addition. Do not derive it inline.

Status tags: `[PRIMARY]` pre-specified primary metric · `[SUPPLEMENTARY]` recorded, not main
narrative · `[POST-HOC]` recomputed after freezing, must be labelled post-hoc ·
`[LIMITATION]` constrains what may be claimed.

Experiment root (read-only): `research-private/experiments/SFibAI-B_AE_COR_v2/`
Round: `AE_COR_v2` · seed 2026 · single seed · 120 epochs per arm.

> **Deliberately absent.** Performance values from the original SFibAI publication
> (Nature Communications 2026) are **not** recorded in this file. They were obtained under a
> different dataset, split, cleaning rule and ROI definition, and must never be numerically
> compared with the present results (`DECISIONS.md` §3.3). Their absence here makes the
> comparison structurally impossible.

---

## 1. Study design

| Fact ID | Value | Definition | Source |
|---|---|---|---|
| `F-DESIGN-SEED` | 2026 | Single random seed; all arms share per-tensor identical initialization for shared modules | `docs/FORMAL_PROTOCOL.md` |
| `F-DESIGN-EPOCHS` | 120 | Epochs per arm, no early stopping | `configs/ae_cor_v2_protocol.yaml` |
| `F-DESIGN-BACKBONE` | ResNet-50, `IMAGENET1K_V2` | torchvision initialization for all arms | `docs/FORMAL_PROTOCOL.md` |
| `F-DESIGN-INPUT` | 512 × 512 | Input resolution; ImageNet normalization | `docs/FORMAL_PROTOCOL.md` |
| `F-DESIGN-BINS` | 36 | Ordinal output bins, scores 0.0–3.5 in steps of 0.1 | `EVALUATION_POLICY.md` |
| `F-DESIGN-GRADEBOUND` | 0.5 / 1.5 / 2.5 | 4-grade boundaries; boundary values fall into the higher grade | `EVALUATION_POLICY.md` |
| `F-DESIGN-OPT` | AdamW, lr 1e-4, weight decay 1e-4, batch 24, AMP, StepLR(step 15, γ=0.6) | Optimizer and schedule | `docs/FORMAL_PROTOCOL.md` |
| `F-DESIGN-LOSS` | α=1.0, β=0.02, γ=0.02, soft-label σ=1.0 | Inherited SFibAI hybrid ordinal grading loss | `docs/FORMAL_PROTOCOL.md` |
| `F-DESIGN-AUXW` | 0.1 / 0.1 | Outer loss weights for position and weak-box branches | `docs/FORMAL_PROTOCOL.md` |
| `F-DESIGN-GATE` | gate_max 0.5, residual_init_scale 0.001 | Gated residual injection hyperparameters, fixed across all arms | `configs/ae_cor_v2_protocol.yaml` |
| `F-DESIGN-DETACH` | `bidirectional_detached` | Gradient boundary between auxiliary branches and grading, fixed across all arms | `configs/ae_cor_v2_protocol.yaml` |
| `F-DESIGN-AUG` | 90°-multiple rotation p=0.7; saturation 0.75–1.25 p=0.5; no flip/crop | Training augmentation; paired arms share sample order and per-sample augmentation | `docs/FORMAL_PROTOCOL.md` |
| `F-DESIGN-SELECT` | Lowest val `R_final` → lowest val image COR → earlier epoch, restricted to epochs 21–120 | Checkpoint selection rule; epochs 1–20 are burn-in and ineligible | `EVALUATION_POLICY.md` |
| `F-DESIGN-HEAD` | Grading head = LayerNorm → Linear(feature→512) → ReLU → Dropout → Linear(512→36); 36-way logits, softmax posterior | The 36-bin posterior is produced by a **single 36-unit linear output layer**, not by binary logistic units | frozen `model.py:60-69`, `prediction.py:38-41` |
| `F-DESIGN-ENV` | Single NVIDIA GeForce RTX 5090 D (CUDA 12.8), PyTorch 2.11.0+cu128, torchvision 0.26.0+cu128, Python 3.10, AMP | Training/inference environment | frozen `runtime_benchmark_results.json` (environment block) + `environment.yml` (python=3.10) |

### 1.1 Arm definitions

| Fact ID | Arm | Configuration |
|---|---|---|
| `F-ARM-A` | A | Stretch resize, no auxiliary branch — the SFibAI baseline |
| `F-ARM-B` | B | Letterbox resize, no auxiliary branch |
| `F-ARM-C` | C | Stretch + position branch |
| `F-ARM-D` | D | Stretch + lesion branch |
| `F-ARM-E` | E | Stretch + position + lesion branches — **SynAP-Fib** |

---

## 2. Cohort and split

Source: `data/processed/schisto_2024_clean_v4/manifests/{images,patients}.csv`

| Fact ID | Split | Images | Patients | Centers | Status |
|---|---|---|---|---|---|
| `F-COHORT-TOTAL` | **all** | **108,709** | **6,373** | **35** | `[PRIMARY]` |
| `F-COHORT-TRAIN` | train | 83,722 | 4,906 | 35 | `[PRIMARY]` |
| `F-COHORT-VAL` | val | 20,880 | 1,227 | 33 | `[PRIMARY]` |
| `F-COHORT-TEST` | test | 4,107 | 240 | 4 | `[PRIMARY]` |

| Fact ID | Value | Definition | Status |
|---|---|---|---|
| `F-SPLIT-PATIENT-OVERLAP` | **0** | Patients shared between train and test — the split is genuinely patient-disjoint | `[PRIMARY]` |
| `F-SPLIT-TEST-CENTERS` | center_05, center_07, center_15, center_17 | Identity of the four test centers | `[PRIMARY]` |
| `F-SPLIT-CENTER-SHARED` | **All four test centers also appear in the training split** | The split is patient-disjoint but center-shared | **`[LIMITATION]`** |

> **`F-SPLIT-CENTER-SHARED` is a hard constraint on claims.** No external-center validation,
> unseen-center generalization, domain-shift robustness, or external institutional holdout may
> be claimed (`DECISIONS.md` §3.4). Must be disclosed in **both** Methods and Limitations.
> Refer to the test set as the **patient-held-out test set**.

### 2.1 Label distribution by split `[PRIMARY]`

Source: `data/processed/schisto_2024_clean_v4/manifests/annotations.jsonl`, fields
`image_label_max` / `patient_label_max`, mapped to 4 grades via `F-DESIGN-GRADEBOUND`.

Image-level:

| Fact ID | Split | F0 | F1 | F2 | F3 | Total |
|---|---|---|---|---|---|---|
| `F-DIST-IMG-TRAIN` | train | 16,182 | 28,020 | 28,427 | 11,093 | 83,722 |
| `F-DIST-IMG-VAL` | val | 3,982 | 7,033 | 7,170 | 2,695 | 20,880 |
| `F-DIST-IMG-TEST` | test | 1,140 | 1,006 | 1,108 | 853 | 4,107 |

Patient-level (`patient_label_max`):

| Fact ID | Split | F0 | F1 | F2 | F3 | Total |
|---|---|---|---|---|---|---|
| `F-DIST-PAT-TRAIN` | train | 854 | 1,161 | 1,977 | 914 | 4,906 |
| `F-DIST-PAT-VAL` | val | 213 | 291 | 495 | 228 | 1,227 |
| `F-DIST-PAT-TEST` | test | **60** | **60** | **60** | **60** | 240 |

| Fact ID | Value | Status |
|---|---|---|
| `F-DIST-TEST-BALANCED` | The test cohort contains **60 patients in each of F0, F1, F2 and F3**. Training and validation follow the cohort distribution, in which F2 is the most frequent patient-level grade. | `[LIMITATION]` |

> **Observation only — no design intent may be asserted.** No document in the workspace records
> why the test cohort has this composition, so the manuscript must not describe it as
> "intentionally balanced", "designed to balance", or "stratified by construction". State only
> the observed counts.
>
> Permitted framing: *Because the test cohort was stage-balanced (60 patients per stage),
> aggregate performance should not be interpreted as a prevalence-weighted estimate for a
> population screening setting.*
>
> Image-level counts are not exactly balanced because patients contribute differing numbers of
> images.

### 2.2 Test set composition

| Fact ID | Value | Definition | Status |
|---|---|---|---|
| `F-TEST-GRADE-DIST` | F0 1,140 · F1 1,006 · F2 1,108 · F3 853 | Image counts by true grade (total 4,107) | `[PRIMARY]` |
| `F-TEST-POSITION-DIST` | p1 694 · p2 699 · p3 689 · p4 671 · p5 682 · p6 672 | Image counts by normalized anatomical position | `[PRIMARY]` |
| `F-TRAIN-POSITION-DIST` | p1 14,137 · p2 14,092 · p3 14,121 · p4 14,047 · p5 13,960 · p6 13,365 | Image counts by position, training split (total 83,722) | `[SUPPLEMENTARY]` |
| `F-VAL-POSITION-DIST` | p1 3,515 · p2 3,524 · p3 3,556 · p4 3,521 · p5 3,478 · p6 3,286 | Image counts by position, validation split (total 20,880) | `[SUPPLEMENTARY]` |
| `F-TEST-CENTER-PATIENTS` | center_05 n=2 · center_07 n=115 · center_15 n=93 · center_17 n=30 | Patients per test center | `[SUPPLEMENTARY]` |

> Position-distribution provenance (added 2026-09-05, P3 fact maintenance): computed once from
> `data/processed/schisto_2024_clean_v4/manifests/images.csv` (columns `split`, `position_norm`).
> The test-split counts reproduce `F-TEST-POSITION-DIST` exactly (cross-validation).

### 2.3 Acquisition protocol `[PRIMARY]`

Added 2026-09-05 per Codex Gate 1 Finding 4 (fact-maintenance). Provenance:
supervisor-confirmed via P1 closure (P1 audit §4 item 1; source document
`data/数据清洗要点-人工标注.md` rule 1, verified verbatim against the predecessor paper's
Data Collection section, NCOMMS tex lines 303–313).

| Fact ID | Value | Definition |
|---|---|---|
| `F-ACQ-PROTOCOL` | Standardized six-position protocol: (1) subxiphoid sagittal plane (left lobe of the liver); (2) left subcostal transverse plane (left lobe and sagittal segment of the portal vein); (3) right subcostal plane (second porta hepatis, confluence of three hepatic veins); (4) right subcostal plane (right hepatic lobe, right hepatic vein, diaphragm); (5) right intercostal oblique plane (right hepatic lobe, portal vein, gallbladder); (6) right intercostal oblique plane (right hepatic lobe, right kidney) | Scanning planes; positions p1–p6 of `F-TEST-POSITION-DIST` |
| `F-ACQ-PER-PLANE` | One to three images are acquired per plane | Per-patient image count is therefore between 6 and 18 before cleaning; every image carries a normalized position label and a fibrosis score |

---

## 3. Evaluation definitions

Source: `SFibAI-B/EVALUATION_POLICY.md`

| Fact ID | Definition |
|---|---|
| `F-DEF-SCORE` | Continuous prediction `ŷ = Σ_k p_k · k/10`, k = 0…35 |
| `F-DEF-COR` | With `e = |ŷ − y|` and `d = |grade(ŷ) − grade(y)|`:<br>`COR = 0.35·e/3.5 + 0.15·I(e>0.3) + 0.15·I(e>0.5) + 0.25·d/3 + 0.10·I(d≥2)`<br>All samples equally weighted. Lower is better. |
| `F-DEF-RFINAL` | `R_final = 0.4·R_image + 0.4·R_patient_max + 0.2·R_center_balanced_patient_max` |
| `F-DEF-RIMAGE` | Mean per-image COR |
| `F-DEF-RPMAX` | COR computed after taking the max over each patient's true and predicted image scores, symmetrically |
| `F-DEF-RCB` | Per-center patient-max COR, aggregated with weights proportional to the square root of each center's patient count. **Purpose: prevent large centers from disproportionately dominating the aggregate patient-level evaluation.** Never described as an external-center or robustness component. |
| `F-DEF-SEVERE` | `severe_error_rate = mean(|ŷ − y| > 1.0)` — defined on the **continuous score**, not on grade distance. Source: frozen evaluator `research-private/experiments/SFibAI-B_AE_COR_v2/round_snapshot/src/sfibai_b/evaluation.py:163`. `EVALUATION_POLICY.md:32` names the metric but does not define it. |
| `F-DEF-TMAE` | `tmae = mean(max(|ŷ − y| − 0.5, 0))` — mean error in excess of a 0.5 tolerance, zero when within tolerance. Source: frozen evaluator `.../round_snapshot/src/sfibai_b/evaluation.py:162`. `EVALUATION_POLICY.md:32` names the metric but does not define it. **Describe it as an excess-error metric beyond a 0.5 tolerance, not as a generic "threshold-weighted MAE".** |
| `F-DEF-WEAKBOX` | Dice/IoU measure agreement with weak bounding boxes. **Must be described as weak-box agreement, never as lesion segmentation ground-truth performance.** |

---

## 4. Primary results — patient-held-out test set

All values: best (validation-selected) checkpoint, test split, seed 2026.
Source: `seed_2026/<arm>/best/test/metrics.json`, cross-checked against
`final_ranking/TEST_SET_MAIN_RESULTS.md`.

### 4.1 Composite endpoint and ranking `[PRIMARY]`

| Fact ID | Arm | Best epoch | `R_final` ↓ | Observed rank |
|---|---|---|---|---|
| `F-RFINAL-E` | E | 103 | **0.186865** | 1 |
| `F-RFINAL-A` | A | 81 | 0.187312 | 2 |
| `F-RFINAL-D` | D | 47 | 0.196686 | 3 |
| `F-RFINAL-B` | B | 39 | 0.198100 | 4 |
| `F-RFINAL-C` | C | 50 | 0.200202 | 5 |

> E is the **best observed** configuration. Its margin over A must never be characterized as a
> demonstrated improvement (`DECISIONS.md` §2).

### 4.2 Image-level metrics `[PRIMARY]`

n = 4,107 images for all arms.

| Fact ID | Arm | Image COR ↓ | MAE ↓ | ±0.3 acc ↑ | ±0.5 acc ↑ | 4-class acc ↑ | macro-F1 ↑ | TMAE ↓ | Severe error ↓ |
|---|---|---|---|---|---|---|---|---|---|
| `F-IMG-A` | A | 0.178900 | 0.379086 | 58.29% | 69.81% | 66.76% | 0.668389 | 0.122417 | 9.08% |
| `F-IMG-B` | B | 0.179921 | 0.382443 | 57.78% | 69.69% | **67.40%** | **0.677572** | 0.123630 | 9.59% |
| `F-IMG-C` | C | 0.181910 | 0.381920 | 56.15% | **70.17%** | 65.89% | 0.662571 | **0.121283** | 9.50% |
| `F-IMG-D` | D | 0.186336 | 0.392331 | 57.12% | 68.86% | 64.23% | 0.643729 | 0.131776 | 10.37% |
| `F-IMG-E` | E | **0.177908** | **0.377857** | 57.95% | 70.15% | 67.03% | 0.671466 | 0.123100 | 9.37% |

### 4.3 Patient-max metrics `[PRIMARY]`

n = 240 patients for all arms.

| Fact ID | Arm | Patient-max COR ↓ | MAE ↓ | ±0.5 acc ↑ | 4-class acc ↑ |
|---|---|---|---|---|---|
| `F-PMAX-A` | A | 0.200569 | 0.430000 | **66.25%** | 64.58% |
| `F-PMAX-B` | B | 0.216948 | 0.450034 | 63.75% | 62.50% |
| `F-PMAX-C` | C | 0.213942 | 0.438725 | 65.83% | 63.75% |
| `F-PMAX-D` | D | 0.211353 | 0.451029 | 64.17% | 63.33% |
| `F-PMAX-E` | E | **0.200528** | **0.420558** | 65.42% | **65.42%** |

### 4.4 Center-balanced patient-max COR `[PRIMARY]`

| Fact ID | Arm | Center-balanced patient-max COR ↓ |
|---|---|---|
| `F-CB-A` | A | 0.177622 |
| `F-CB-B` | B | 0.196765 |
| `F-CB-C` | C | 0.209305 |
| `F-CB-D` | D | 0.188052 |
| `F-CB-E` | E | **0.177453** |

---

## 5. Auxiliary branch outputs `[PRIMARY]`

Source: `seed_2026/<arm>/best/test/metrics.json`

### 5.1 Position branch (arms C and E)

| Fact ID | Arm | Accuracy ↑ | macro-F1 ↑ | Cross-entropy ↓ | n |
|---|---|---|---|---|---|
| `F-POS-C` | C | 66.40% | 0.662250 | 0.944391 | 4,107 |
| `F-POS-E` | E | **66.81%** | **0.665861** | **0.916542** | 4,107 |

Six-class normalized anatomical position. Ground-truth position is used **only** as a training
supervision signal; grading always reads the predicted posterior.

Per-class position recall `[SUPPLEMENTARY]`, source `metrics.json` field `position.recall_<k>`:

| Fact ID | Arm | p1 | p2 | p3 | p4 | p5 | p6 |
|---|---|---|---|---|---|---|---|
| `F-POSREC-C` | C | 0.8141 | 0.6309 | 0.5327 | 0.5618 | 0.6569 | 0.7872 |
| `F-POSREC-E` | E | 0.8473 | 0.6509 | 0.5457 | 0.5261 | 0.6686 | 0.7679 |

### 5.2 Lesion branch (arms D and E)

| Fact ID | Arm | Weak-box Dice@0.5 ↑ | Weak-box IoU@0.5 ↑ | Valid boxes |
|---|---|---|---|---|
| `F-LES-D` | D | 0.353920 | 0.226066 | 4,035 |
| `F-LES-E` | E | **0.360312** | **0.235487** | 4,035 |

Weak-box agreement, not segmentation ground truth (`F-DEF-WEAKBOX`).

### 5.3 Gate statistics — mechanistic diagnostic `[SUPPLEMENTARY]`

| Fact ID | Arm | Branch | Mean | SD | P10 | P50 | P90 |
|---|---|---|---|---|---|---|---|
| `F-GATE-C-POS` | C | position | 0.097689 | 0.011298 | 0.086365 | 0.094788 | 0.114185 |
| `F-GATE-D-LES` | D | lesion | 0.002344 | 0.003434 | 0.001769 | 0.002234 | 0.002876 |
| `F-GATE-E-POS` | E | position | 0.084124 | 0.011330 | 0.072815 | 0.080933 | 0.101379 |
| `F-GATE-E-LES` | E | lesion | 0.006513 | 0.017638 | 0.003479 | 0.004543 | 0.006386 |

> Permitted use: confirming the anatomical residual pathways remained active rather than
> collapsing to zero. **Gate magnitude alone does not establish contribution size**, because
> the effective contribution also depends on residual feature magnitude. Do not present gate
> values as evidence of how much the injection contributed.

---

## 6. Computational cost `[PRIMARY]`

Source: `preflight/model_cost/model_cost.json`
Measurement: batch = 1, 3 × 512 × 512; Conv2d and Linear only, two FLOPs per MAC;
CUDA AMP eager, 10 warmup and 30 measured iterations.

| Fact ID | Arm | Parameters | vs A | GFLOPs | vs A | Latency median (ms) | Latency P90 (ms) |
|---|---|---|---|---|---|---|---|
| `F-COST-A` | A | 24,579,684 | — | 42.709 | — | 3.031 | 3.356 |
| `F-COST-B` | B | 24,579,684 | +0 | 42.709 | +0.0% | 2.989 | 3.350 |
| `F-COST-C` | C | 24,610,739 | +31,055 | 42.709 | +0.0% | 3.521 | 4.010 |
| `F-COST-D` | D | 25,991,302 | +1,411,618 | 43.918 | +2.8% | 3.607 | 4.245 |
| `F-COST-E` | E | 26,022,357 | **+1,442,673 (+5.9%)** | 43.918 | **+2.8%** | 3.993 | 4.427 |

---

## 7. Post-hoc recomputed metrics `[POST-HOC]`

Recomputed from frozen `seed_2026/<arm>/best/test/predictions_full.csv.gz` by
`scripts/recompute_posthoc.py`. **Must always be described as post-hoc, never as
pre-specified.** No model, checkpoint, or selection decision was touched.

**Validation gate: 35/35 checks passed** across all five arms (n, MAE, ±0.3 accuracy,
±0.5 accuracy, 4-class accuracy, severe error rate, `cor_severe_stage`), each agreeing with
the frozen `metrics.json` to within 1e-6 (independently re-derived by the Gate 0 reviewer at
maximum absolute delta 0). Output: `tables/posthoc_validation.csv`.

> **Scope of the gate.** It verifies unique image IDs, test-split membership, finite values,
> arm identity and the frozen row count, then compares prediction-derived scalars against
> `metrics.json`. It does **not** compare image IDs against the Data V4 test manifest.
> Do not describe it as an independent dataset-membership audit. Cohort membership was
> verified separately from the manifests (§2).

### 7.1 Stage-wise MAE — Figure 3a

| Fact ID | Arm | F0 | F1 | F2 | F3 |
|---|---|---|---|---|---|
| `F-STAGEMAE-A` | A | 0.196508 | 0.416107 | 0.514474 | 0.403570 |
| `F-STAGEMAE-B` | B | 0.215458 | 0.387597 | 0.496175 | 0.451800 |
| `F-STAGEMAE-C` | C | 0.215293 | 0.394219 | 0.510325 | 0.423316 |
| `F-STAGEMAE-D` | D | 0.223659 | 0.416849 | 0.517423 | 0.426352 |
| `F-STAGEMAE-E` | E | 0.196277 | 0.411035 | 0.516525 | 0.401280 |

Support: F0 1,140 · F1 1,006 · F2 1,108 · F3 853 (`F-TEST-GRADE-DIST`), identical for all arms.

> **Report as observed.** The pattern must not be pre-framed as concentrated in any particular
> stage (`DECISIONS.md` §3.2 — "先画结果，再解释结果").

### 7.2 Stage-wise recall — Figure 3b

From frozen `metrics.json` (`grade_f<k>_recall`), not recomputed. Status: `[PRIMARY]`.

| Fact ID | Arm | F0 | F1 | F2 | F3 |
|---|---|---|---|---|---|
| `F-STAGEREC-A` | A | 80.18% | 49.50% | 63.63% | 73.27% |
| `F-STAGEREC-B` | B | 77.37% | 55.47% | 65.79% | 70.22% |
| `F-STAGEREC-C` | C | 76.32% | 53.38% | 62.91% | 70.57% |
| `F-STAGEREC-D` | D | 77.63% | 46.92% | 60.65% | 71.40% |
| `F-STAGEREC-E` | E | 81.14% | 50.50% | 63.63% | 72.10% |

Support as in `F-TEST-GRADE-DIST`.

> **Report as observed.** Note that the lowest-recall stage (F1) and the highest stage-wise
> MAE stage (F2) differ. Do not collapse these into a single claim that "intermediate stages
> are hardest" — the two metrics identify different stages, and both must be stated as
> measured.

### 7.3 36-grade image-level QWK `[POST-HOC]`, supplement only

#### Citable values — `[POST-HOC | MANUSCRIPT]`

Quadratic weighted Cohen's κ computed after mapping the continuous posterior expectation to
the nearest of the 36 valid grades: `clip(rint(score/0.1), 0, 35)`, quadratic weights.
This follows the manuscript's own prediction rule (`F-DEF-SCORE`).

| Fact ID | Arm | QWK ↑ |
|---|---|---|
| `F-QWK-A` | A | 0.864009 |
| `F-QWK-B` | B | 0.857924 |
| `F-QWK-C` | C | 0.861988 |
| `F-QWK-D` | D | 0.854622 |
| `F-QWK-E` | E | **0.864566** |

Required Methods/Supplement sentence (or close paraphrase):

> Continuous posterior-expectation predictions were mapped to the nearest one of the 36 valid
> grades before computing quadratic-weighted Cohen's κ; posterior argmax predictions were not
> used.

#### Audit-only value — `[AUDIT-ONLY | DO-NOT-CITE]`

| Fact ID | Arm | QWK under posterior argmax |
|---|---|---|
| `F-QWK-ARGMAX-A` | A | 0.847942 |

> **Do not cite this value anywhere in the manuscript or supplement.** It exists solely to
> document that an independent recomputation using the stored posterior-argmax `pred_bin`
> field yields a different number — the two prediction rules disagree on 1,601 of 4,107 test
> images. Recorded for provenance if a reviewer recomputes QWK under the argmax rule.

---

## 8. Supplementary metrics `[SUPPLEMENTARY]`

### 8.1 Image-level discrimination and calibration

| Fact ID | Arm | macro AUROC ↑ | macro AUPRC ↑ | Brier ↓ | ECE ↓ |
|---|---|---|---|---|---|
| `F-AUC-A` | A | 0.888217 | 0.718714 | 0.493755 | 0.175061 |
| `F-AUC-B` | B | 0.887697 | 0.724624 | 0.485416 | 0.170211 |
| `F-AUC-C` | C | 0.884395 | 0.711592 | 0.503889 | 0.183766 |
| `F-AUC-D` | D | 0.879815 | 0.706133 | 0.519752 | 0.188694 |
| `F-AUC-E` | E | **0.891698** | **0.729264** | **0.474036** | **0.164196** |

### 8.2 Patient-median COR

| Fact ID | Arm | Patient-median COR ↓ |
|---|---|---|
| `F-PMED-A` | A | 0.163623 |
| `F-PMED-B` | B | 0.159540 |
| `F-PMED-C` | C | 0.168302 |
| `F-PMED-D` | D | 0.167317 |
| `F-PMED-E` | E | **0.154344** |

Robustness analysis only — patient-max is the pre-specified patient-level aggregation.

### 8.3 Paired bootstrap — supplement only

10,000 center-stratified patient-cluster paired bootstrap replicates, shared draws across
arms; percentile 95% CI. Source: `final_ranking/paired_patient_cluster_bootstrap.csv`.
Pre-registered contrasts. A negative delta favours the candidate.

| Fact ID | Contrast | Observed Δ | Bootstrap mean ± SD | 95% CI | P(candidate better) |
|---|---|---|---|---|---|
| `F-BOOT-AB` | A − B | −0.010789 | −0.010804 ± 0.005689 | [−0.021909, +0.000310] | 0.971 |
| `F-BOOT-CA` | C − A | +0.012890 | +0.012920 ± 0.005234 | [+0.002762, +0.023122] | 0.007 |
| `F-BOOT-DA` | D − A | +0.009374 | +0.009370 ± 0.005784 | [−0.001717, +0.020827] | 0.052 |
| `F-BOOT-EA` | E − A | −0.000447 | −0.000447 ± 0.006116 | [−0.012287, +0.011826] | 0.533 |
| `F-BOOT-EC` | E − C | −0.013337 | −0.013367 ± 0.005631 | [−0.024376, −0.002223] | 0.990 |
| `F-BOOT-ED` | E − D | −0.009821 | −0.009817 ± 0.005542 | [−0.020718, +0.001010] | 0.961 |

> `P(candidate better)` is the proportion of bootstrap replicates in which the candidate
> achieved a lower `R_final`. **It is not a frequentist p-value** — this clarification must
> accompany the supplementary table. The main text may cite at most one or two of these CIs
> (`DECISIONS.md` §4.3).

### 8.4 Per-center patient-max COR — Supplementary Figure S1 `[SUPPLEMENTARY]`

Source: `paper_plot_packs/seed_2026/<arm>/best_test/center.csv`, field `cor`.

| Fact ID | Center | Patients | A | B | C | D | E |
|---|---|---|---|---|---|---|---|
| `F-CENTER-05` | center_05 | 2 | 0.003978 | 0.106383 | 0.445622 | 0.004904 | 0.005329 |
| `F-CENTER-07` | center_07 | 115 | 0.184925 | 0.188137 | 0.180888 | 0.170010 | 0.183879 |
| `F-CENTER-15` | center_15 | 93 | 0.279634 | 0.316480 | 0.310589 | 0.326305 | 0.281672 |
| `F-CENTER-17` | center_17 | 30 | 0.028546 | 0.026213 | 0.025597 | 0.027244 | 0.025816 |

| Fact ID | Value | Status |
|---|---|---|
| `F-CENTER-05-UNSTABLE` | For center_05 (n=2) the patient-max COR ranges from 0.003978 to 0.445622 across the five arms — a spread exceeding two orders of magnitude. This demonstrates directly that estimates from very small centers are unstable. | `[LIMITATION]` |

> Per-center values are **descriptive only** — all four test centers appear in the training
> split (`F-SPLIT-CENTER-SHARED`). Never present them as generalization or robustness evidence.
> Do not describe center_05's low COR under any arm as good performance.
>
> **`F-CENTER-05-UNSTABLE` is `[AUDIT-ONLY]` for the two-orders-of-magnitude spread.** The
> manuscript may state that center_05 contributed only two patients and that small-center
> estimates are descriptive; it must **not** report the cross-arm spread as a finding
> (`DECISIONS.md` §5.1).

### 8.5 Checkpoint selection diagnostic

| Fact ID | Value |
|---|---|
| `F-SELECT-AGREE` | For arms A, B, D and E the validation-selected best checkpoint also outperformed that arm's epoch-120 last checkpoint on test |
| `F-SELECT-C-INVERT` | Arm C is the sole exception: best test `R_final` 0.200202 versus last test 0.191930. The pre-registered rule was followed without post-hoc substitution. |

### 8.6 Figure 4 source data `[SUPPLEMENTARY]`

Added 2026-09-05 (P3 fact maintenance). Provenance: frozen
`paper_plot_packs/seed_2026/<arm>/best_test/confusion.csv` and `calibration.csv`
(read-only). Row sums of each confusion matrix reproduce `F-TEST-GRADE-DIST`
exactly (cross-validation).

Four-grade confusion matrices (rows = true grade, columns = predicted grade; image level, n = 4,107):

| Fact ID | Arm | Matrix (F0–F3 rows) |
|---|---|---|
| `F-CONF-A` | A | [914, 187, 39, 0] / [278, 498, 212, 18] / [32, 244, 705, 127] / [2, 30, 196, 625] |
| `F-CONF-E` | E | [925, 175, 40, 0] / [287, 508, 201, 10] / [28, 259, 705, 116] / [1, 28, 209, 615] |

Calibration (reliability diagrams):

| Fact ID | Value |
|---|---|
| `F-CAL-SOURCE` | Per arm, `calibration.csv` gives, for each of the four grades and 10 equal-width probability bins, the mean predicted probability and the observed frequency of that grade. The reliability diagrams in Figure 4 plot mean predicted probability (x) against observed frequency (y), one series per grade, directly from these frozen files. |

### 8.7 Supplementary-figure source data `[SUPPLEMENTARY]`

| Fact ID | Value |
|---|---|
| `F-SUPP-S1` | Per-center patient-max COR, arms A–E, from §8.4 (Figure S1 renders `F-CENTER-05…17` with patient counts 2/115/93/30 on the axis) |
| `F-SUPP-S2` | Error distributions: per-image absolute error from frozen `errors.csv` (all 4,107 test images per arm); Figure S2 shows the histogram of absolute error, arms A and E |
| `F-SUPP-S3` | Training/checkpoint trajectories: per-epoch validation `R_final` from the frozen history bundles (`seed_2026/<arm>/history/`), epochs 1–120; the selected epoch is marked. No smoothing. |

---

## 9. Integrity status

| Fact ID | Value |
|---|---|
| `F-AUDIT-GATE` | `SEED_2026_GATE.json` records `status: PASS`, with paired-initialization checks OK for shared modules across all five arms (324 tensors), position modules across C/E (12 tensors) and lesion modules across D/E (12 tensors); `runtime_benchmark_selection_verified: true`; `performance_outcome_gate_applied: false`. **The file carries no timestamp**, so the execution date of the gate cannot be verified from the artifact itself. Do not state a run date in the manuscript. |
| `F-AUDIT-COMPLETE` | All five arms have 120-row history, 120 validation epoch bundles, best/last checkpoints, complete best/last val/test bundles and `RUN_COMPLETE.json` |
| `F-AUDIT-FP32` | The FP16 overflow in the D/E lesion head was corrected per `SNAPSHOT_AMENDMENT_20260903_FP32_LESION.md`, without altering model structure, loss, data, optimizer or evaluation rules |
| `F-AUDIT-CROSSMODEL` | **Independent cross-model integrity audit has not been executed.** A machine gate PASS must not be described as an independent review PASS. |

---

## 10. Required citation

| Fact ID | Value |
|---|---|
| `F-CITE-SFIBAI` | Xu Z., Zhang J., Wu T., Hua H., Yang K., Zeng T. *Deep learning for precision grading of Schistosoma japonicum-induced liver fibrosis in ultrasound images.* Nature Communications, 2026. DOI: 10.1038/s41467-026-76287-9 |

Published 2026-08-21 as an early citable version. **Volume, issue and article number are not
yet assigned — do not invent them.** Cite for methodological provenance only; see
`DECISIONS.md` §3.3.

---

## 10.1 Supervisor-confirmed provenance facts (P1 resolution, 2026-09-04)

Confirmed by the project owner in response to the P1 fact-method audit
(`P1_FACT_METHOD_AUDIT.md`, questions A–F). Candidate historical text was extracted from the
published predecessor paper's final revision
(`D:\PhD\liver-Fibrosis\Final Revision\Final Submisson\NCOMMS-25-30891C-main.tex`) and
verified against `SFibAI-Final2/`. These facts are now citable in the manuscript.

| Fact ID | Fact | Status |
|---|---|---|
| `F-ETHICS-BOARD` | The study protocol was approved by the Ethics Review Committee of the Jiangsu Institute of Parasitic Diseases (Approval ID: JIPD-2019-017). | `[CONFIRMED]` — supervisor answer A; Data V4 belongs to the same original cohort covered by this approval |
| `F-ETHICS-CONSENT` | All participants provided written informed consent prior to enrolment. Participants did not receive compensation. Sex and gender were not collected and were not considered in the study design. | `[CONFIRMED]` — supervisor answer A |
| `F-ETHICS-NOTIME` | No acquisition time window is stated in the manuscript. The supervisor directed that actual acquisition time not be written. | `[CONFIRMED]` — supervisor answer B |
| `F-COHORT-INCLUSION` | Enrolment followed the predecessor study's criteria: participants were enrolled from schistosomiasis-endemic counties in Jiangsu Province, China, covering the full severity spectrum — individuals with confirmed *S. japonicum* infection history, registered advanced schistosomiasis patients, and non-infected controls. | `[CONFIRMED]` — supervisor answer C ("按照 NC 的标准"). **Write qualitatively; do not import the predecessor paper's cohort counts (9,588 / 5,462 / 4,126) — Data V4 retains its own counts (6,373 patients after cleaning).** |
| `F-GRADE-STANDARD` | The four-grade clinical scale derives from the Handbook of Schistosomiasis Control (3rd ed.) and the Chinese diagnostic criteria for schistosomiasis (WS 261–2006); correspondence with international guidelines (Niamey protocol) is described in the WHO-chaired Basel ultrasonography protocol (2025). | `[CONFIRMED]` — supervisor answer D |
| `F-QC-PROCESS` | Quality control as in the predecessor paper (anonymized): annotating physicians underwent two rounds of unified municipal- and provincial-level training; a coordinating group centrally reviewed the labels, provided corrective feedback on discrepancies, and re-evaluated a subset of cases under blinded review; the target overall discrepancy rate was below 5%, and cases with major disagreements were jointly reviewed to consensus. | `[CONFIRMED]` — supervisor answer D. **Anonymized wording only** — no names, no counts, no batch mappings (`DECISIONS.md`-inherited constraint, P1 audit part 0) |
| `F-FUNDING` | National Natural Science Foundation of China, grant nos. 82173586 and 82373644. | `[CONFIRMED]` — supervisor answer E |
| `F-COI` | The authors declare no competing interests. | `[CONFIRMED]` — supervisor answer E |
| `F-AVAIL-CODE` | The SFibAI-B codebase is under local git management (remote `github.com/StatXzy7/SFibAI-B`); public release is planned. Manuscript wording: code "will be made publicly available upon publication" — **do not cite a release URL or archive DOI that does not yet exist**. | `[CONFIRMED]` — supervisor answer F |
| `F-AVAIL-DATA` | Data availability follows the predecessor model: the full clinical dataset is not publicly available (patient-derived images under ethics approval and privacy protection); de-identified data for verifying main findings available under restricted access subject to institutional approval and a data-use agreement, requests to the corresponding authors. | `[CONFIRMED]` — supervisor answer F, reusing predecessor statement scope |

### Reference entries confirmed for reuse

Verified verbatim in `SFibAI-Final2/References.bib` (lines 464, 474, 670):

- `MOH2000SchistoManual` — Disease Control Department of Chinese Ministry of Health, *Chinese Schistosomiasis Control Manual*, 3rd ed., Shanghai Science and Technology Press, 2000 (in Chinese).
- `MOH2006SchistoCriteria` — Ministry of Health of the People's Republic of China, *Chinese diagnostic criteria for schistosomiasis (WS 261–2006)*, 2006 (in Chinese).
- `richter2025basel` — Richter et al., "The Basel ultrasonography protocol for assessing hepatosplenic pathologies in Asian schistosomiasis: report of a WHO expert meeting," *Infectious Diseases of Poverty*, **14(1): Article 83, 2025**. DOI: 10.1186/s40249-025-01349-x. (2026-09-05 correction: the earlier "14(4):67–76" record inherited from the predecessor's bibliography was wrong; Crossref is the authority. **Full 17-author list per Crossref** (count re-verified programmatically; an earlier note here said 16 in error): Richter, Neumayr, Garba-Djirmay, Ohmae, Aniceto, Zhou, Xu, Guo, Ning, Kamau, Tamarozzi, Wu, King, Vennervald, Chami, Utzinger, Hatz.)

---

## 11. Open items

Deferred by design — these are needed only when the corresponding artifact is produced, and
each must be added here (not computed inline) before that artifact is drafted.

| Item | Needed for | Status |
|---|---|---|
| Validation `R_final` at the selected epoch, per arm | Checkpoint-selection subsection | Deferred to Phase 1 |
| Per-class AUROC/AUPRC/Brier/ECE; complete patient-max and patient-median metric groups; position per-class recall and predicted frequency | Supplementary tables | Deferred to Phase 1 |
| A/E four-grade confusion-matrix cells; reliability-bin counts, confidence and accuracy | Figure 4 | Deferred until Figure 4 is built (source CSVs verified present) |
| Error-distribution bins; per-epoch training trajectories | Supplementary Figures S2, S3 | Deferred until those figures are built |
| Approved case identifiers with true/predicted scores and position outputs | Figure 5 | Deferred to supervisor node B |
| Six-position distribution for train and validation splits | Figure 2 | Deferred until Figure 2 is built |
| Device / scanner metadata | Table I, if required | Not located in Data V4 manifests; request only if Table I needs it |

| Process item | Status |
|---|---|
| Codex Gate 0 provenance audit | **PASS** — round 1 FAIL with 7 findings; all closed; round 2 closure re-audit returned PASS with no remaining blocker |
| Supervisor node A sign-off | Pending |
| P1 fact-method audit | **RESOLVED (2026-09-04)** — supervisor answered questions A–F; facts recorded in §10.1; candidate historical evidence released for manuscript use. Residual items: Figure 2 position distributions (deferred), availability wording pending public code release decision |

### Gate 0 round 1 — findings and resolutions

| # | Finding | Resolution |
|---|---|---|
| 1 | `F-DEF-SEVERE` attributed to `EVALUATION_POLICY.md`, which names but does not define it | Re-attributed to frozen evaluator `evaluation.py:163`; value was already correct |
| 2 | `F-DEF-TMAE` cited a nonexistent policy definition and described the metric imprecisely | Replaced with the implemented formula `mean(max(err − 0.5, 0))` from `evaluation.py:162` |
| 3 | `F-AUDIT-GATE` claimed a 2026-09-04 run date that no artifact supports | Rewritten to report only what `SEED_2026_GATE.json` contains; run date removed |
| 4 | Bibliographic date/DOI provenance unverified | Left as supplied by the project owner, who confirmed it against the publisher page; to be re-checked via WebFetch during bibliography construction |
| 5 | FACTS.md incomplete for the frozen manuscript structure | Cohort totals, per-split label distributions, bootstrap mean/SD and per-center COR added; remaining gaps scheduled above |
| 6 | QWK discretization route underspecified (argmax vs rounded expectation differ on 1,601/4,107 images) | Discretization now stated explicitly with the argmax variant's value disclosed |
| 7 | Recompute script cited "DECISIONS.md, decision 12", which does not exist | Docstring reference corrected |
