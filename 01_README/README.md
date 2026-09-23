# RTAS Public Repo — Governance Files

This folder contains the protocol history, configuration history, changelog, and checksums for the RTAS study.

> **Post-audit status.** The v0.2 protocol/config files below are historical freeze records.
> For current manuscript numbers, use `../06_RESULTS/19_numerical_provenance_ledger.csv`,
> `../manuscript/data_verification.tex`, and the root `README.md`.

## Files

| File | Content |
|------|---------|
| `FINAL_ANALYSIS_PROTOCOL.md` | Historical v0.2 freeze protocol; retained for provenance and containing superseded first-batch/pre-audit values |
| `final_config.yaml` | Historical v0.2 machine-readable freeze config; retained for provenance, not current post-audit numbers |
| `CHANGELOG.md` | Versioned changes to the protocol/config |
| `CHECKSUMS.md` | MD5 hashes of frozen artefacts per milestone (v1.1 addendum: submission figure set + compiled snapshot + provenance ledger) |

## Repository structure

```
RTAS/
├── 01_README/            ← governance (this folder)
├── 02_FIGURES/           ← full engineering figure set: 9 main (incl. standalone 8a/8b) + 5 supplementary
│   ├── main/
│   └── supplementary/
├── 03_CODE/              ← reproducible analysis scripts (01–22)
├── 05_VALIDATION/        ← validity-program artefacts (150-pair ratings, agreement stats, baselines)
├── 06_RESULTS/           ← frozen aggregate outputs + 115-check provenance ledger
├── manuscript/
│   ├── figures/          ← 7 main + 5 supplementary files/panels (S1, S2, S3a, S3b, S4)
│   ├── preview/          ← compiled paper snapshots
│   └── data_verification.tex  ← ready-to-insert verification blocks (Methods + Tables S3–S4)
└── archive/internal_history/  ← superseded Markdown working drafts (provenance only)
```

The manuscript LaTeX master is maintained on Overleaf; this repository mirrors
the submission figures, the compiled snapshot, and the verification fragment.

## Key numbers (v1.1 post-audit frozen; 115/115 independently verified)

| Number | What it is |
|--------|------------|
| 3,714 | UIETP projects (innovation-training + entrepreneurship-training tracks) |
| 56,901 | OpenAlex papers (WHU, article type, 2020–2024) |
| 60,615 | Joint corpus for BERTopic (= 3,714 + 56,901) |
| 33,312 | Matched papers (58.5% of 56,901) |
| 886 | BERTopic non-outlier topics (+ 1 OUTLIER = 887 CSV rows) |

Note: "12,000" = old incomplete first-batch pool (superseded; aggregation
selection only). "35,721" = label frequency sum (NOT a paper count).

## Golden rules

1. Figures are outputs of `03_CODE/` only. Never hand-edit.
2. Every script in `03_CODE/` reads frozen CSVs from the private data store; never hardcode stats.
3. Never hand-edit numbers in the manuscript. For post-audit reconciliation, the numerical provenance ledger and frozen analysis outputs take precedence over historical v0.2 documentation.
4. `01_DATA/raw_private/` (in the private store) = read-only archival.
5. Every freeze milestone bumps protocol version + tags Git + regenerates CHECKSUMS.
6. No personal names in repo-facing outputs: raters are referred to as "Rater A" / "Rater B" (see CHANGELOG, v1.1-postaudit-repo round).
