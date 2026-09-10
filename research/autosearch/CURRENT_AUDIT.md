# Current implementation audit — TEST PENDING

This is source and software evidence, not a completed experiment or an external
review verdict. HEAD initially matches 356576445f51c7b2b302b46f339658377682262d;
20 tracked code/ files were dirty (388 insertions, 216 deletions) and eight LUA
files untracked. Preserved as user work. Full initial patch is private outside
this repository; SOURCE_BASELINE/ROUND_LOCK bind actual dependencies.

| Question | Evidence and finding | Executable check |
|---|---|---|
| Auxiliary gradient topology | code/src/sfibai_b/model.py SFibAIModel.forward detaches global features before position_head; _lesion_logits_fp32 detaches C4; predicted probabilities/attention are detached before injection | gradient_matrix, test_independent_gradient_axes_and_actual_head_update |
| A versus F | F has heads and losses but no grading injection; no auxiliary gradient reaches backbone. Shared A/F FP32 gradient equality is tested with same tensors, no clipping. This does not assert full AMP run identity | test_a_f_shared_gradients_fp32 |
| G slow start | loss.py aux_scale_for_epoch is zero through20 and full at40. With legacy detach it does not directly warm up shared auxiliary gradients | legacy schedule tests, pruning protection |
| Six positions | data.py __getitem__ maps numeric 1..6 to CE targets0..5. No verified anatomical names supplied; retain codes. Actual counts are in DATA_AUDIT | data audit validates missing/unknown codes and dev counts |
| Lesion semantics | data.py _lesion_target selects max-label box union and checks max equals image label. Not all lesions, not contour truth. Other lower-grade boxes cannot be general negative evidence | data audit counts lower boxes and mismatches; local head ignores unknown/ambiguous pixels |
| Negative semantics | loss.py _box_components uses labels>0 in bin units: excludes0.0 only, includes0.1–0.4 in clinical F0 | test_zero_only_excluded_not_clinical_f0 |
| KL boundaries | loss.py _grading_components clamps five nearby indices; bin0 gathers0 three times, bin35 gathers35 three times. MSE and boundary terms use bin units, not score units. Boundary bucketization right=True | test_legacy_kl_clamp_duplicates_are_preserved; named cdf adds separate loss only |
| Continuous evaluation | prediction.py expected bin/10; evaluation.py score_to_grade right=True; _patient_predictions true/pred symmetric; _center_balanced_patient_max sqrt(n) | legacy evaluation suite and test_canonical_patient_max_and_center_weighting |
| Input ROI provenance | workspace scripts/datasets/build_schisto_2024_clean_v1.py extract_roi_label (line702) uses image grayscale mean threshold, border cleanup, largest contour only. process_image_file calls it with image path. build_schisto_2024_clean_v2.py roi_box/crop_image_to_tmp use ultrasound ROI metadata, not lesion boxes | source audit; same existing ROI input for every model |
| Dataset curation | v2 annotation_rule_reasons used box/label quality filters for retention. This is historical annotated-cohort curation; exhaustive negatives and contours are not established | no new claim of unselected raw-image clinical performance |
| Test auto evaluation | runner.py run_task has a train_only return but defaults false and otherwise creates test dataset and best/last evaluation. queue.py and gate.py expect old test bundles | new training never imports legacy runner/queue/gate/ranking; test-access rejection tests |
| Legacy runtime coupling | training.py TaskSpec locks LUA seed/arms/120 and RuntimeSelection only4/6/8 workers; snapshot.py binds old runtime and gate fields; benchmark.py has old300-batch/eager policy | new dataclasses/loader support workers0; no widening of old ARM_BRANCHES |
| Prediction storage | storage.py saves canonical metrics and per-image CSV, atomic JSON. New infer reuses collector/evaluator and labels high-resolution weak-box mapping explicitly | three-output contract and canonical regression tests |
| Historical results | docs/PROVENANCE.md identifies code import and frozen paper sources. paper/en/tables remains historical material; no old score is supplied to optimization | original artifacts preserved, research output paths ignored |

Full data hash audit runs independently. Until DATA_AUDIT status is PASS, do not
state that counts, identities or all pixels were verified. Anatomical names and
exhaustive annotation completeness remain unverified even after identity PASS.

No test performance has been computed for this round. Costs and auxiliary quality
are measured during actual runs; CPU synthetic behavior is not research evidence.

## Executed local evidence (2026-09-11)

- All 108709 image content hashes matched. Native train/val/test counts matched
  83722/20880/4107 images,4906/1227/240 patients,35/33/4 centers. No cross-split
  patient or image-hash overlap was found. Manifest and annotation SHA256 match
  the canonical protocol; no annotation/image max-label mismatch or missing
  image annotation was found.
- All109882 annotations declare rectangle.909 boxes are below their image's
  max grade;181 images have exact score0.0. These counts do not establish
  exhaustive lesion annotation or absence of unannotated pathology.
- Train position1..6 counts:14137,14092,14121,14047,13960,13365. Validation:
  3515,3524,3556,3521,3478,3286. Names remain unverified. Inner train/val contain
  66929/16793 images and no patient is shared.
- First128 inner-train images had mean channel spread4.397/255; this sample
  does not justify claiming saturation always has no effect or eliminating the
  baseline augmentation. Rot90 versus conservative augmentation remains a
  recipe comparison with six-class metrics, not an assumed direction.
- New suite45 passed; legacy targeted suite29 passed,1 skipped (its remote
  configured data path is absent locally),1 existing tensor-conversion warning.
- Real8x512 maximum FPN decoder FP32 smoke: two finite optimizer updates,
  peak allocated CUDA memory4584638976 bytes; separate BF16 loss/gradients finite.
  This is stability evidence, not a throughput benchmark or model-quality result.
- Full raw evidence is in ignored outputs/DATA_AUDIT.json,GRADIENT_TOPOLOGY.json,
  SMOKE.json and private command logs. FINAL_MANIFEST is produced only after
  actual120-epoch three-seed confirmation; it does not yet exist.
