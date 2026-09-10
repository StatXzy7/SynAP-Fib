# SynAP-Fib finite three-task search

Independent research package; read PROTOCOL.md and CURRENT_AUDIT.md first.
All private artifacts go to ignored outputs/. Set SYNAP_DATA_ROOT and optionally
SYNAP_OUTPUT_ROOT, or let configuration discover the existing ancestor Data V4.
Use the CUDA Python environment for real training; CPU smoke requires no weights
download. Runtime currently tested locally with the cv environment.

From the SynAP-Fib repository:

```powershell
python -m pip install -e code
python -m pip install -e research/autosearch
python -m synap_search audit --config research/autosearch/configs/default.yaml
python -m synap_search smoke --config research/autosearch/configs/default.yaml
python -m pytest research/autosearch/tests -q
python -m synap_search search --config research/autosearch/configs/default.yaml --resume
python -m synap_search confirm --config research/autosearch/configs/default.yaml
python -m synap_search freeze --config research/autosearch/configs/default.yaml
# Use the actual manifest path printed by successful freeze:
python -m synap_search final-test --manifest PATH_TO_FINAL_MANIFEST
python -m synap_search report --manifest PATH_TO_FINAL_MANIFEST
```

`run-all --config ... --resume` advances only after the prior stage succeeds.
No feasible candidate blocks confirmation/freeze/test. `report --config ...`
writes truthful pending status before a manifest exists. No dummy frozen manifest
is generated to make the command appear successful. No automated push is made.

There is no dependency on old queue state or chat memory. SQLite studies, trial
proposals, RNG/optimizer/scaler/EMA checkpoints and source hashes support resume.
Scientific changes cannot resume an existing trial. Model forward takes images
only. Deployment entry is synap_search.models.image_outputs plus geometric
inverse and predicted_regions in synap_search.data.

The initial registry implements M1–M4, two gradient axes, C4/FPN decoders,
three predicted fusion modes, sparse local severity, legacy/CDF loss, two resize
and augmentation recipes. Optional teachers, patient-aware objectives, caches,
new backbone tracks and resampling are not enabled. Software smoke is not a
real training result. Final research success is not guaranteed.
