# SynAP autosearch v1 — preregistered implementation protocol

Status: TEST PENDING. This new round implements REQUEST.md, independent of LUA_v1
and AE_COR_v2. Historical test exposure is true. Test is closed to search from
this round onward; historical blindness cannot be restored.

## Authority and immutable sources

Reference and initial HEAD: 356576445f51c7b2b302b46f339658377682262d.
Branch: research/synap-autosearch-v1. Initial code/ contains uncommitted LUA work;
it is preserved. Exact imported runtime source hashes are saved by preflight and
ROUND_LOCK; an editable install is not a frozen historical reconstruction.
Neither code/, reproducibility/, original data nor paper tables are edited here.
A_legacy and E_reference mean faithful current A/E functions under this round's
paired runtime, not reproductions of old paper numbers.

## Data boundary

Independent audit validates locked manifest/annotation SHA256, native counts,
patient separation, cross-split image hashes, all image content hashes, numeric
position classes, annotation geometry and max-grade consistency. Expected native
train/val/test: 83722/20880/4107 images, 4906/1227/240 patients, 35/33/4 centers.
The auditor may inspect test identity and duplicates, never model performance.
Search receives only a sanitized train/val manifest with exact required columns,
per-partition annotation files and audited hashes. It never invokes old runner,
queue, gate, ranking, or old result readers. This is application-level isolation,
not an operating-system sandbox against a malicious process with disk access.

Inner validation comprises 20% of native train patients, sorted by SHA256 of
31001:patient_uid; remaining patients form inner train. Derived parent images
stay with patients. All selection-stage fits, including any future teacher or
cache, must follow this partition. Native val is used only for confirmation.
Inner train supplies pixel statistics. Missing annotation is unknown. There is
no contour truth or established exhaustive normal/background annotation.

## Objective and controls

Canonical evaluator is reused unchanged. R_final = .4 image COR + .4 symmetric
patient-max COR + .2 center-balanced patient-max COR, with sqrt(patient count)
center weights. Lower is better. Symmetric patient-median is separately reported.
Score is posterior-weighted bin / 10; four-class boundaries .5/1.5/2.5 enter the
higher class. Epochs 1–20 never qualify for best. Later checkpoints minimize
(R_final, image COR, epoch), lexicographically. No early stopping.

A_legacy: grading-only ResNet50, legacy loss/data recipe. A_tuned: same grading
architecture, 8 recipe opportunities. E_reference/M0: exact legacy E adapter,
retrained on inner train, selected on inner val for the reference. M0 aliases E
and does not spend another trial. All share ImageNet1K V2 ResNet50 pretraining,
component initialization seeds, sample order for equal recipes and one runtime.
No medical checkpoint, pseudolabel teacher or external patient data is used.

Auxiliary constraints are separate from grading. At each selected checkpoint,
require position macro-F1 AND mean max-grade weak-box IoU at threshold .5 to be
at least E_reference under the same development protocol. Missing metrics fail.
No compensating weighted sum; tolerances are both zero. In confirmation and
test compare arithmetic means across fixed paired seeds with the corresponding
E_reference on that split. Record all six recalls/frequencies and confusion
matrix. No development absolute threshold is transported to test.

## Mechanisms and gradient axes

M1: auxiliary heads genuinely sharing ResNet50, no injection. M2: M1 plus C4
decoder or top-down C2–C5 FPN, width 64/128, stride 8/4. M3: M2 plus predicted
position and lesion local features, feature residual/logit residual/soft
six-posterior low-rank experts. M4: M3 plus sparse per-box local severity logits;
unannotated pixels and conflicting differently graded box overlaps are ignored.
This local severity branch is training-only. It is not patient-max label copying.

Independent auxiliary→backbone and grading→prediction scales use
stopgrad(h)+eta*(h-stopgrad(h)), eta in {0,.1,.3,1}. Warm-up {0,10,20} scales
auxiliary loss linearly to full weight. G_slow faithfully retains the old 20→40
schedule with detached heads and is never pruned. New residual final layers
start small, with no zero multiplicative gate that would kill learning.
Legacy hybrid is unchanged; named cdf candidate adds .1 mean squared CDF error
over 36 bins. This differentiable surrogate is not canonical COR.

## Budget and advancement

Development seed 31001. Full horizon is always 120; scheduling never compresses
to rung length. Budget: E control plus 8 A_tuned recipes; 24 mechanism trials;
8 recipe trials on the best feasible mechanism. Select two unique candidate
configurations from completed feasible mechanism/recipe trials. First six
mechanism trials include M1/M2/M3/M4/G and run to completion. Compute 30/60 versus
120 rank correlation on these six; pruning enables only if both Spearman >= .5.
Otherwise use full training inside the same trial-count caps. Rungs 30/60/120;
no pruning until warm-up + 10 effective epochs. Rung lists and correlations are
separate records. Never call a pruned trial feasible. A baseline recipe and
candidate recipe each have 8 full-horizon resource opportunities; 24 extra
mechanism trials are disclosed separately, not called matched total compute.

Optuna 4.9.0 TPESampler (6 startup trials), SQLite persistent study and sampler
state; SuccessiveHalvingPruner(min_resource=30,reduction_factor=2). Constraints
are explicit controller checks, not a deprecated or prune-dependent constraints
API. Registry records failed/pruned/completed trials; same trial only resumes
with identical config, source, environment and development files. Scientific
patches require a new round/trial identity. Scheduler position, optimizer,
scaler, EMA, RNG and history are restored from last checkpoint.

Confirm both shortlisted candidates, A_legacy, A_tuned and E_reference using
native train, native val, seeds [34001,34002,34003], each 120 epochs. Select one
candidate on native-val feasibility and mean R_final, deterministic name tie.
No feasible candidate means test stays closed. No seed picking or ensemble.

## Data and runtime recipes

Primary ResNet50/36-bin semantics fixed. Stretch or centered letterbox, geometric
inverse stored. Legacy rotation/saturation or conservative ±7 degree rotation,
gamma/contrast/brightness/noise. Never flip by default or use GT input crops.
All target maps transform with images; local unknown stays ignore. Native files
read-only. No MixUp/CutMix, local crop relabeling, patient-aware loss, resampling,
distillation, pseudomasks, PCGrad, large backbone or ensemble in this initial
finite registry. These are optional future tracks, not silently enabled features.
Cache-key utility exists; image caching is not enabled in this implementation.

LR log[3e-5,3e-4], head multiplier {1,3,10}, WD log[1e-6,1e-3], StepLR(15,.6)
or 5-epoch warm-up cosine over 120, EMA {off,.999}, auxiliary weights
{.03,.1,.3}. Default FP32, batch8, workers0/eager; CPU zero-worker smoke valid.
Real maximum decoder FP32 updates and BF16 finite gradients are measured before
search. BF16 is measured separately and not silently selected. No compile or DDP
claim. One GPU/one controller, exclusive controller lock; do not preempt jobs.
All-head batch1 decode-to-output latency, parameters, training wall/GPU allocation
time and peak allocated memory are saved; no auxiliary head is disabled to time
the new three-task system. Baseline A intrinsically has one task.

## Frozen evaluation and outputs

Before test freeze configs, seed list, code/environment/data fingerprints, best
checkpoint hashes, preprocessing, .5 region threshold, 8-connectivity, EMA
selection, no calibration/ensemble, and comparison list. Primary comparison:
one native-val-selected new candidate minus A_tuned. A_legacy, E_reference and
auxiliary comparisons are secondary. Manifest integrity is checked before any
test dataset construction. Test closes search permanently for this round.

Lesion map means max-grade evidence weak-box agreement, not all-positive lesion
segmentation. Existing .5 Dice/IoU use probabilities area-resampled to 32x32,
then exact old target nearest-resize semantics; native resolution agreement is
separate. Region boxes are predicted .5 connected components mapped to ROI
coordinates with confidence from component mean probability, no GT routing.
Raw image inputs are already dataset ultrasound ROI crops. Pixel-only ROI source
code is separately audited; retained-image selection historically used annotation
quality filters, which does not make the crop a lesion-box prompt.

Report all paired seed deltas, mean/sample SD/directions and center-stratified
patient-cluster bootstrap, 10000 draws shared across models and seeds. CI is for
the average of these fixed seeds; seed×patient are never independent units.
Negative mean is point-estimate improvement; negative CI upper bound with all
seed directions negative is stronger conditional evidence. Both still require
auxiliary constraints, image-only outputs and intact protocol; neither validates
external clinical utility or precise contour segmentation.

## Software evidence versus experiment evidence

Unit tests and synthetic CPU smoke establish software behavior only. DATA_AUDIT,
GRADIENT_TOPOLOGY and SMOKE record actual execution. Search, confirmation, freeze
and final-test must actually finish their gates before any completion claim.
No placeholder FINAL_MANIFEST is executable. FINAL_REPORT starts test-first and
states pending until all frozen model/seed test bundles exist.

API references: https://optuna.readthedocs.io/en/v4.9.0/reference/samplers/generated/optuna.samplers.TPESampler.html
and the installed optuna.pruners.SuccessiveHalvingPruner signature.
