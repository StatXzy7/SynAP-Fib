# SynAP-Fib ICLR rewrite plan

## New paper identity

**Working title:** Learning Anatomical Concepts for Interpretable Fine-Grained Ultrasound Grading: A Study in Schistosomiasis-Associated Liver Fibrosis

**Central question:** Can training-time anatomical supervision be converted into image-derived concepts that a fine-grained grading model can consume and expose at inference?

**Positioning:** A task-specific, non-bottleneck concept pathway for medical vision. The ResNet-50 backbone is a controlled experimental platform, not the contribution. The paper does not claim a universal explanation method, cross-disease transfer, or architecture independence.

## Evidence currently available

- Five frozen configurations, one seed (2026), one ResNet-50 backbone.
- Test ranking by prespecified `R_final`: E 0.186865, A 0.187312, D 0.196686, B 0.198100, C 0.200202.
- E is best observed; E and A are not distinguishable on the primary endpoint.
- Position output: 66.81% accuracy, 0.6659 macro-F1, CE 0.9165.
- Weak-box agreement: Dice 0.3603, IoU 0.2355 over 4,035 valid boxes.
- E overhead: +5.9% parameters, +2.8% arithmetic, 3.031 ms to 3.993 ms median latency.

## Claims allowed in this draft

1. The model learns two semantically supervised image-derived concepts.
2. The concepts can be consumed at inference without anatomical metadata.
3. The joint concept pathway is best observed in the frozen comparison.
4. The interface is intervention-ready because concept representations are explicit.

## Claims deliberately deferred

- Faithful explanation.
- Causal use of concepts.
- Necessity or sufficiency of either concept.
- Physician utility.
- Cross-disease, unseen-center, cross-backbone, or multi-seed generalization.

## Figure plan

1. Architecture: image, shared ResNet-50, position and lesion concepts, gated residual interface, grading output; annotate the interface as replaceable.
2. Concept learning: position confusion matrix, weak-box overlays, concept quality metrics.
3. Primary test comparison: full ranking and patient-level metrics.
4. Qualitative outputs: image, predicted concepts, grading output; label as descriptive, not intervention evidence.
5. Future/required intervention figure: predicted, ground-truth, shuffled, masked, and corrected concepts with paired prediction changes. This should be added before an ICLR submission if the paper is to claim faithful interpretability.

## Required next experiments for a stronger ICLR submission

1. Ground-truth concept replacement at the interface.
2. Concept masking and shuffled-concept controls.
3. Clinician-corrected or synthetic concept edits on a fixed test subset.
4. Multi-seed replication.
5. Optional second backbone after the intervention result is established.

The current ICLR draft intentionally does not invent these results. It states the interpretability boundary explicitly and preserves the existing frozen evidence.

