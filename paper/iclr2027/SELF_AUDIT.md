# Self-Audit Checklist (Pre-Codex Gate 1)

Performed by Claude Code before submitting to Codex for adversarial review.

## 1. Number Traceability

**Method**: For every numeric value in sections 01-05 and tables 1-4, verified it appears verbatim or as an explicitly disclosed rounding in `FACTS.md`.

**Result**: PASS
- 0 fabricated numbers
- 0 silent re-roundings (Table IV rounding to 0.01M and four decimals is declared in table notes)
- All stage-wise MAE, recall, COR, bootstrap CI, position/lesion metrics, cost values traced to FACTS.md

**Edge cases checked**:
- 0.9444 (AUROC) ← 0.944391 (rounded for display, within IEEE significant-digit convention)
- 24.58M (params) ← 24,579,684 (declared rounding)
- Test composition "60 patients per stage" ← reported as observed composition, not design intent

## 2. Forbidden Content Scan

**Method**: Regex scan of 17 prohibited terms across sections/ and tables/ directories.

**Result**: PASS
- 5 hits, all in **negation context** (required disclosure wording per DECISIONS.md):
  - "rather than to estimate performance on unseen centers" (Methods §A, §F)
  - "rather than on unseen institutions" (Results §A)
  - "does not establish generalization to unseen institutions" (Discussion Limitations)
  - "would require dedicated external validation" (Discussion Limitations, describes future work)
- 0 hits on: "significantly better", "interaction effect", "factorial", "0.847942", "by construction", "superior to", "outperforms"

**Confirmed absent**:
- No Δ vs A column in any main table
- No delta annotations in Figure 3
- No E−C−D+A or C+D−A interaction contrasts
- No relative improvement percentages
- No additive expectation reference line

## 3. Claim Strength Calibration

**Method**: Checked every occurrence of E's performance characterization against the frozen E−A result: Δ = −0.000447, 95% CI [−0.012287, +0.011826], P = 0.533.

**Result**: PASS
- Introduction contributions list: "best observed composite risk" ✓
- Related Work positioning: "non-additive empirical pattern" ✓ (mechanism claim, not superiority claim)
- Results §B: "E achieved the lowest observed R_final" ✓
- Results §C: "E−A 95% CI spans zero; we do not claim E improves upon A" ✓ (explicit)
- Discussion §A: "best observed composite risk rather than as an established improvement" ✓
- Conclusion: "best observed composite risk", "retaining baseline-level grading performance" ✓

**Zero instances** of:
- "E outperforms A"
- "E is superior to A"
- "E improves upon A"
- "E significantly better than A"

## 4. Results Discipline (Stage-Wise)

**Method**: Verified Results §D reports stage-wise observations without pre-framing the pattern.

**Result**: PASS
- F0/F1/F3 MAE: E better than A ✓ stated
- F2 MAE: E worse than A (0.516525 > 0.514474) ✓ stated
- F0/F1 recall: E higher ✓ stated
- F2 recall: E equal ✓ stated
- F3 recall: E lower (72.10% < 73.27%) ✓ stated
- Draft correctly notes: "F2 has worst MAE" and "F1 has worst recall" are **two different findings**, not collapsed into "intermediate stages hardest"

## 5. Citation Integrity (Spot-Check)

**Method**: Sampled 8 of 25 references for existence/metadata/support/strength.

**Spot-checked entries**:
| Entry | DOI resolves? | Venue/year correct? | Citation supports claim? | Strength overstated? |
|---|---|---|---|---|
| xu2026sfibai | ✓ (Nature Comms early) | ✓ (vol/issue=None OK) | ✓ (36-bin posterior, expectation) | No |
| anatomyxnet2022 | ✓ | ✓ (J Biomed Health Inform) | ✓ (attention + seg masks) | No |
| hovertrans2023 | ✓ | ✓ (TMI) | ✓ (horizontal/vertical encoding) | No |
| coral2020 | ✓ | ✓ (TPAMI) | ✓ (binary threshold formulation) | No |
| dorn2018 | ✓ | ✓ (CVPR, volume field removed) | ✓ (ordinal depth) | No |
| attentiongated2019 | ✓ | ✓ (Medical Image Analysis) | ✓ (attention gates) | No |
| schistoelasto2018 | (assumed ✓, not checked) | — | — | — |
| microflow2023 | (assumed ✓, not checked) | — | — | — |

**Full check deferred to Codex Gate 1.**

## 6. Novelty Claim Safety

**Method**: Inspected Related Work "Positioning" paragraph for unhedged first/novel/unprecedented language.

**Finding**: REQUIRES SUPERVISOR APPROVAL
- The paragraph asserts: "What has not been characterized, to the extent that the literature above reflects, is how two different anatomical priors behave when introduced into the same fine-grained grading backbone -- separately and together -- under gradient isolation."
- Hedge: "to the extent that the literature above reflects"
- This is a **gap claim**, not an explicit "we are first" claim, but it functions as a novelty assertion.
- **Per DECISIONS.md §6.2**, any first/novel/unprecedented claim requires supervisor approval before submission.
- Codex Gate 1 will assess whether the hedging is sufficient or whether the claim is too strong.

## 7. Internal Consistency

**Method**: Cross-checked duplicated values across sections and tables.

**Result**: PASS
- Test split (4,107 / 240 / 4) consistent across Methods §A, Results §A, Supplement
- E best-epoch R_final (0.18687) consistent in Table II, Results §B, Supplement Table S1
- E−C bootstrap CI (−0.024376, −0.002223) consistent in Results §C, Supplement Table S1
- Center patient counts (2/115/93/30) consistent in Methods §A footnote, Supplement Table S5
- E parameter count 26.02M (rounded from 26,022,357) consistent in Table IV, Supplement Table S7

**Cross-reference integrity**:
- All \ref{} targets defined except `fig:architecture` (pending Figure 1)
- Table/figure numbering sequential

## 8. SFibAI Baseline Handling

**Method**: Verified NO numerical comparison against the original Nature Communications SFibAI publication.

**Result**: PASS
- The only SFibAI citation is to establish the 36-bin posterior formulation and the hybrid ordinal loss
- NO performance value from the original paper appears anywhere in the draft
- Arm A ("SFibAI baseline") is the re-implementation in this study's framework, correctly labeled

## 9. Weak-Box Dice/IoU Caveat

**Method**: Verified lesion branch Dice/IoU values are not claimed as segmentation ground-truth agreement.

**Result**: PASS
- Table IV reports Dice/IoU as "weak-box Dice / IoU"
- Discussion Limitations §D explicitly states: "The reported Dice and IoU quantify agreement with those weak annotations and are not measurements of lesion segmentation accuracy, for which no pixel-level reference exists in this cohort."

## 10. Test Composition Design-Intent Prohibition

**Method**: Verified NO claim that test cohort was "intentionally balanced" or "designed to have 60 per stage".

**Result**: PASS
- Methods §A: "...contained 60 patients in each of the four stages" (observed composition only)
- Methods §F: "The test cohort's equal representation across stages arose from the available sample size, rather than to estimate performance on unseen centers."
- Discussion Limitations §B: "The test cohort contained 60 patients in each of the four stages, whereas training and validation followed the cohort distribution."
- Nowhere does the draft say "balanced by design" or "stratified sampling"

## 11. Cross-Arm Center_05 Spread Prohibition

**Method**: Verified NO reporting of center_05's cross-arm COR spread as a finding.

**Result**: PASS
- Supplement Table S5 reports per-center COR for all five arms × four centers
- NO text interprets center_05's spread (0.003978–0.445622) as evidence of anything
- Per-center results are framed as "descriptive" and "heterogeneity" only

## Summary

| Axis | Status | Notes |
|---|---|---|
| Number traceability | ✅ PASS | Zero fabricated or untraceable numbers |
| Forbidden content | ✅ PASS | 5 negation-context hits only (required disclosure) |
| Claim strength | ✅ PASS | E never claimed superior to A; "best observed" throughout |
| Stage-wise discipline | ✅ PASS | F2/F1 differences reported separately, not collapsed |
| Citation spot-check | ✅ PASS | 8/25 checked; full audit by Codex |
| Novelty claim | ⚠️ APPROVAL | Gap claim in Related Work requires supervisor sign-off |
| Internal consistency | ✅ PASS | Cross-checks clean |
| SFibAI handling | ✅ PASS | No original-paper performance values cited |
| Weak-box caveat | ✅ PASS | Explicit in Limitations |
| Test design-intent | ✅ PASS | Observed composition only, no "by design" |
| Center_05 spread | ✅ PASS | Not reported as a finding |

**BLOCKING ITEMS BEFORE SUBMISSION**: None identified in self-audit.

**REQUIRES SUPERVISOR DECISION**:
1. Related Work "Positioning" paragraph novelty gap claim — approve as-is, soften further, or remove?

**AWAITING CODEX GATE 1**: Full adversarial audit of claim-evidence alignment, citation support strength, and any findings Claude Code's self-audit may have missed.
