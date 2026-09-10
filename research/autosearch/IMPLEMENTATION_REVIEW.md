# Implementation review record

Scope: new research/autosearch package against reference3565764; legacy dirty
code/ excluded from edits. These are code reviews, not independent experiment
integrity review or research-completion verdicts.

## Standards axis

Initial findings: report bypassed bundle verification; resume could skip rung
decision; sampler file write was non-atomic. Fixed with common verify_bundle,
replayed persisted halving decisions, and atomic sampler/proposal storage.
Follow-up found mid-proposal RNG-position drift. Fixed with official independent
TPE sampling seeded by trial number/parameter name, and regression test comparing
uninterrupted/resumed later proposals beyond TPE startup. Reviewer inspected this
fix and reported no remaining HIGH/CRITICAL finding in reviewed changes.

## Spec axis

Initial findings: report bypassed bundle hashes; final auxiliary acceptance
missing; CUDA/BF16 gate insufficient; predicted-box localization metric missing.
Fixed with common verification, explicit fixed-seed auxiliary mean comparisons
and conditional-evidence labels, environment/batch/precision smoke gate, and
predeclared max-grade box mean best IoU/recall. Reviewer inspected remediation
and reported no remaining material blocker in these fixes for CUDA/batch8/512.

## Verification boundary

Parent executed the tests; reviewers did not independently rerun reported GPU
smoke or full tests. The review does not establish successful120-epoch training,
complete search, final freeze, test improvement or clinical benefit. Source
fingerprints bind runtime and prohibit silently repairing a running trial.
