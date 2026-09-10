# DECISIONS.md — SynAP-Fib TMI manuscript

Frozen editorial decisions from the pre-drafting supervisor interview (2026-09-04).

`FACTS.md` governs **what is true**. This file governs **what may be written, and how** —
even when a statement is technically true.

Any change to a decision in this file requires supervisor approval. Writing agents may not
relax, reinterpret, or work around them.

---

## 1. Venue and identity

| Item | Value |
|---|---|
| Target venue | IEEE Transactions on Medical Imaging (TMI), first submission |
| Method name | **SynAP-Fib** (Synergistic Anatomical Priors) |
| Working title | *SynAP-Fib: Synergistic Anatomical Priors for Fine-Grained Ultrasound Liver Fibrosis Grading in Schistosomiasis* |
| Template | `IEEEtran` (`journal` option), non-anonymous |
| Language | English for all manuscript content (body, captions, supplement). Chinese only for supervisor-facing progress reports and Codex review summaries. |

---

## 2. Core positioning

The paper does **not** claim that SynAP-Fib outperforms the SFibAI baseline.

The claim is:

> Under a clinically aligned three-view risk evaluation protocol, introducing either
> anatomical prior alone degrades grading performance, whereas their joint configuration
> retains baseline-level grading accuracy while additionally producing anatomical position
> and lesion localization outputs at small computational cost.

Consequences:

- Configuration E is described as the **best observed** configuration, never as a
  statistically established improvement over A.
- The E-vs-A near-tie is disclosed honestly in Limitations.
- "Synergistic" refers to the **empirical pattern** that single priors degrade while the
  joint configuration does not. It is not asserted as a formal statistical interaction.

---

## 3. Forbidden content (hard constraints)

Writing agents must not produce any of the following.

### 3.1 Forbidden derived quantities

| Forbidden | Reason |
|---|---|
| The interaction contrast `I = E − C − D + A` | Post-hoc four-term combination without pre-registered uncertainty; deliberately excluded from the manuscript |
| Additive expectation `C + D − A` | Same |
| A `Δ vs A` column in any main table | Would foreground the weakest number (E−A = −0.00044) |
| Δ annotations or additive reference lines in Figure 3 or any main figure | Same, in graphical form |
| Relative improvement percentages vs the baseline (e.g. "0.24% better") | Not supported at this effect size |
| **Any quantitative value not present in `FACTS.md`** | Single-source-of-truth rule (§5) |

### 3.2 Forbidden terminology

| Forbidden | Use instead |
|---|---|
| "interaction effect", "factorial interaction analysis", "2×2 factorial design" | "complementary behavior", "joint benefit", "non-additive empirical pattern", "a 2×2 comparison of position and lesion priors" |
| "significantly better", "significant improvement" (vs baseline) | "best observed", "retained baseline-level performance" |
| "proven", "demonstrates that ... causes" | "consistent with", "plausible" |
| "first", "novel to our knowledge", "unprecedented", "no prior work" | Requires separate supervisor approval (§6.2) |
| Any wording implying applicability to non-schistosomal fibrosis (viral, alcoholic, NAFLD/MAFLD) | Always scope to schistosomiasis-associated fibrosis |
| "external center", "external-center holdout", "unseen center", "unseen institution", "center shift", "domain shift", "external validation", "held-out center" | See §3.4 — structurally false for Data V4 |
| "held-out test set" (ambiguous) | **"patient-held-out test set"** |

### 3.4 No external-center claim (Data V4)

**No claim of external-center validation, unseen-center generalization, cross-center domain
shift robustness, or external institutional holdout is permitted for Data V4.**

Verified split structure:

- Patient overlap between train and test: **0** — the split is genuinely patient-disjoint.
- Test centers: `center_05`, `center_07`, `center_15`, `center_17`.
- **All four test centers also appear in the training split.**

The earlier `paper-plan/` documents describe an "external-center holdout" and an
`external_test` split. That setting belonged to the superseded `clean_v2` dataset and **does
not hold for Data V4**. Those documents must not be used as a source for split description.

Rationale: the danger is not the absence of external centers — it is multicenter data being
written up as external validation.

Consequences:

- `R_center_balanced_patient_max` is described **only** as "center-balanced patient-max COR",
  whose purpose is to prevent large centers from disproportionately dominating the aggregate
  patient-level evaluation. It is never described as an external-center or robustness
  component.
- Per-center results are **descriptive**, never generalization evidence.
- Disclosed in **both** Methods (as fact) and Limitations (as scope constraint).

### 3.3 Forbidden comparisons

Performance values from the original SFibAI publication **must never** be numerically
compared with results obtained under the present Data V4 protocol. The datasets, splits,
ROI cropping and cleaning rules all differ.

Those values are deliberately **absent from `FACTS.md`**, so the comparison is structurally
impossible rather than merely prohibited.

SFibAI may be cited **only** for methodological provenance and prior task formulation.

Required Methods sentence (or close paraphrase):

> The SFibAI baseline was retrained from scratch under the present Data V4 preprocessing,
> split, and evaluation protocol; consequently, its performance in this study should not be
> directly compared with values reported under the original SFibAI experimental setting.

---

## 4. Structure

### 4.1 Main tables (four)

| Table | Content |
|---|---|
| I | Cohort and split characteristics |
| II | Main grading performance, arms A–E: `R_final`, Image COR, MAE, ±0.5 acc, 4-class acc, Patient-max COR, Patient-max MAE |
| III | 2×2 prior configuration (A/C/D/E): Position prior, Lesion prior, `R_final`, Image COR, Patient-max COR. **No Δ column.** |
| IV | Auxiliary outputs (position accuracy/macro-F1, weak-box Dice/IoU) and computational cost (parameters, FLOPs, latency). **Gate statistics live in the Supplementary Material** — decided at supervisor node A.5, because gate magnitude alone cannot establish contribution size. |

### 4.2 Main figures (five)

| Figure | Content |
|---|---|
| 1 | Architecture: backbone, position head, lesion head, gated residual injection, bidirectional detach. **Authored in draw.io** — keep both `figures/fig1_architecture.drawio` and the exported `figures/fig1_architecture.pdf`. Draw **only mechanisms that exist**: backbone → position/lesion branches → gated residual injection → grading head, with `bidirectional detach` marked. Do **not** depict no-gate or gradient-coupled variants, and do not let the layout imply that internal components were individually ablated — they were not. |
| 2 | Cohort flow and label/position distributions across splits |
| 3 | **Stage-wise performance of the baseline and SynAP-Fib** — A vs E only. (a) stage-wise MAE, (b) stage-wise recall. Support annotated in the caption. No Δ marks. |
| 4 | Confusion matrices and reliability diagrams, A vs E |
| 5 | Qualitative cases: original image + lesion attention + predicted position/score, F0–F3 plus a failure case. Given the freed page space, this figure is generously sized. |

Supplementary figures:

| Figure | Content |
|---|---|
| S1 | **Per-center descriptive performance on the patient-held-out test set.** Caption must state: *All test centers were represented in the training split; therefore, these results characterize center-wise performance heterogeneity rather than generalization to unseen centers.* Axis labels carry patient counts. Title must not contain "robustness" or "generalization". |
| S2 | Error distribution analysis |
| S3 | Training and checkpoint-selection trajectories |

### 4.3 Statistics placement

- The paired bootstrap analysis lives **entirely in the supplement**.
- The main text may cite **at most one or two** confidence intervals, only where the
  complementary-behavior narrative requires support.
- `P(candidate better)` may appear only in supplementary table notes, always with the
  clarification that it is a bootstrap proportion and **not** a frequentist p-value.

### 4.4 Supplementary content

Paired bootstrap contrasts; AUROC/AUPRC/Brier/ECE; patient-median metrics; per-center
breakdowns; QWK; full per-class metrics.

### 4.5 Section structure

Related Work is an **independent Section 2**, not folded into the Introduction.

| Section | Responsibility |
|---|---|
| 1. Introduction | clinical/task gap → fine-grained grading challenge → why anatomical information matters → SFibAI limitation → SynAP-Fib idea → contributions |
| 2. Related Work | what has been done, and why SynAP-Fib is not a trivial combination of existing multi-task / anatomy-informed learning |
| 3. Methods | dataset, preprocessing, architecture, losses, training protocol, evaluation definitions |
| 4. Results | Tables I–IV, Figures 3–5 |
| 5. Discussion | interpretation, then tiered Limitations (§5.1) |
| 6. Conclusion | |

Related Work has exactly three subsections:

1. Ultrasound liver fibrosis grading
2. Ordinal and fine-grained medical image prediction
3. **Anatomy-informed and auxiliary-supervised learning** — the emphasis; roughly half the
   section, covering the 3–5 genuinely close works that decide novelty positioning

**Related Work performs positioning only.** It states structural and problem-setting
differences. It must not preview experimental outcomes — no "unlike prior work, our method
achieves superior performance", and no comparative performance statement of any kind.

Rationale for a separate section: this paper's novelty risk lies not in performance but in
how far the anatomical-prior / auxiliary-supervision / gated-residual design differs from
existing work. The close works need room to be distinguished individually, and a dedicated
section makes the Gate 3 novelty audit tractable.

---

## 5. Single source of truth

`FACTS.md` is the only permitted source of quantitative content.

1. **Any quantitative statement not present in `FACTS.md` is forbidden.**
2. Writing agents **must not compute any number themselves** — not even a subtraction of two
   values that are both in `FACTS.md`.
3. If a needed value is missing, the agent must stop and request its addition through the
   Phase 0 fact-maintenance process rather than deriving it inline.

Every fact carries one of three status tags:

| Tag | Meaning |
|---|---|
| `[PRIMARY]` | Pre-specified primary metric (`R_final`, COR, MAE, ±0.5, 4-class accuracy) |
| `[SUPPLEMENTARY]` | Recorded but not part of the main narrative (AUROC, ECE, patient-median, per-center) |
| `[POST-HOC]` | Recomputed after freezing — stage-wise MAE, 36-grade QWK. Must be described as post-hoc; never presented as pre-specified. |
| `[LIMITATION]` | A fact that constrains what may be claimed (e.g. the center-shared split). Must be reflected in Methods and Limitations. |
| `[AUDIT-ONLY \| DO-NOT-CITE]` | Recorded for provenance only. **Must never appear in the manuscript or supplement.** |

---

## 5.1 Limitations must be tiered, not enumerated flat

`FACTS.md` carries four `[LIMITATION]` facts. They must **not** become four equally weighted
self-deprecating paragraphs. Write **three thematic paragraphs**:

| Paragraph | Content |
|---|---|
| 1 | Etiological scope (schistosomiasis only) **and** the absence of unseen-center external validation (`F-SPLIT-CENTER-SHARED`) |
| 2 | Test cohort composition — stage-balanced at 60 patients per stage (`F-DIST-TEST-BALANCED`), and heterogeneous center sample sizes. `F-CENTER-05-UNSTABLE` is **folded into this paragraph in one clause at most**; it is primarily a supplementary figure caption matter. |
| 3 | Single prespecified backbone — generalization across alternative architectures remains to be established (`F-AUDIT-CROSSMODEL`) |

Wording rules:

- Do **not** state in the manuscript that per-center COR varied by two orders of magnitude
  across arms. `n = 2` is self-evidently insufficient; amplifying it only creates a negative
  impression without informing the reader.
- Do **not** use internal engineering vocabulary such as "cross-model audit was not performed".
  Write: *The proposed design was evaluated with the prespecified ResNet-50-based framework,
  and its robustness across alternative backbone architectures remains to be established.*
- Do **not** assert design intent for the test cohort composition (see `F-DIST-TEST-BALANCED`).

---

## 6. Failure protocols

### 6.1 Claim–evidence mismatch (Codex Gate 1)

ToolSearchs may autonomously fix factual and grammatical errors. **Any change to the strength,
scope, novelty, clinical interpretation, or causal meaning of a claim requires supervisor
approval.** Flag and report; do not self-adjust.

### 6.2 Insufficient neighboring literature

If fewer than 3–5 genuinely close anatomy-informed / auxiliary-supervision works are found,
report to the supervisor with databases searched, exact queries, keyword families, date
range, near-miss works found, and why each falls short.

**"Not found" must never be converted into a novelty claim.** Every `first` / `novel` /
`unprecedented` / `no prior work` assertion requires separate supervisor approval.

### 6.3 Recomputation mismatch

Any disagreement between recomputed validation checks and frozen metrics **invalidates all
downstream manuscript generation until resolved**. Rounding must never be assumed as the
explanation. Investigate arm/checkpoint correspondence, missing rows, grade mapping,
aggregation, filtering, and metric implementation before proceeding.

*Applied once already: the initial `severe_error_rate` check failed because the script used
grade distance ≥ 2 rather than the policy definition |error| > 1.0. Root cause identified and
corrected; all 35 checks now pass.*

---

## 7. Repository safety

The working tree's git state is unreliable (`git log` fails despite `.git` existing).

**No git operations are permitted for the entire workflow** — no `add`, `commit`, `checkout`,
`reset`, `clean`, or `branch`. ToolSearchs may only create and modify files inside
`paper-plan/05_manuscript/synap_fib_tmi_20260904/` and read from the frozen experiment tree.

The frozen experiment tree is **read-only**.

---

## 8. Bibliography

- Target 45–60 references — a guideline driven by relevance, never a quota to fill.
- Every reference must be traceable to a trusted bibliographic source, preferably DOI, PMID,
  DBLP, or an official publisher/guideline record. **No citation may be generated solely from
  model memory.**
- DOIs are not required where they do not exist (WHO documents, clinical guidelines).
- Five groups must be covered: (i) SFibAI provenance, (ii) clinical basis for schistosomal
  fibrosis ultrasound assessment, (iii) ordinal / fine-grained grading methods,
  (iv) multi-task / auxiliary supervision / anatomical priors, (v) weakly supervised
  localization and attention.
- **Group (iv) receives disproportionate search effort** — novelty positioning depends on
  finding 3–5 genuinely close works.
- No relationship-driven citations (collaborators, likely reviewers).

Required citation, provenance only:

> Xu Z., Zhang J., Wu T., Hua H., Yang K., Zeng T. *Deep learning for precision grading of
> Schistosoma japonicum-induced liver fibrosis in ultrasound images.* Nature Communications,
> 2026. DOI: 10.1038/s41467-026-76287-9

Volume, issue, and article number are **not yet assigned** (early citable version). Do not
invent them.

---

## 9. Workflow

```
Phase 0  FACTS.md + DECISIONS.md + recomputation   -> Codex Gate 0 -> supervisor node A
Phase 1  Methods || Results (+ table/figure skeleton)             -> supervisor node A.5
         Figure 5 candidate cases                                 -> supervisor node B
         Introduction + Related Work (after Results frozen)
         Discussion + Limitations + Conclusion      -> Codex Gate 1
Phase 2  Integration, bibliography, LaTeX build     -> Codex Gate 2 (terminology/overclaim)
                                                    -> Codex Gate 3 (TMI reviewer audit)
                                                    -> supervisor node C
```

Execution is performed by Claude Code agents; **all review is performed by Codex** via
`mcp__codex__codex` (see `AGENTS.md` §5). The executor's own model family must never serve as
reviewer.

Codex Gate 3 additionally audits citations on four axes: existence, metadata correctness,
whether the cited location genuinely supports the sentence, and whether any related work's
conclusions are stated more strongly than the original paper claimed.
