# RTAS Public Repo — Governance Files

This folder contains the protocol, configuration, and changelog for the RTAS study.

## Files

| File | Content |
|------|---------|
| `FINAL_ANALYSIS_PROTOCOL.md` | v0.2+ single source of truth for sample, RTAS, pipeline |
| `final_config.yaml` | Machine-readable parameter sheet (v0.2+) |
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
│   ├── figures/          ← 12 submission figures named as in the paper (7 main + S1–S4)
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
3. Never hand-edit numbers in the manuscript. If a number does not match, the frozen CSV wins.
4. `01_DATA/raw_private/` (in the private store) = read-only archival.
5. Every freeze milestone bumps protocol version + tags Git + regenerates CHECKSUMS.
6. No personal names in repo-facing outputs: raters are referred to as "Rater A" / "Rater B" (see CHANGELOG, v1.1-postaudit-repo round).
