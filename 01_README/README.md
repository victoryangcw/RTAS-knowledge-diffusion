# RTAS Public Repo — Governance Files

This folder contains the protocol, configuration, and changelog for the RTAS study.

## Files

| File | Content |
|------|---------|
| `FINAL_ANALYSIS_PROTOCOL.md` | v0.2+ single source of truth for sample, RTAS, pipeline |
| `final_config.yaml` | Machine-readable parameter sheet (v0.2+) |
| `CHANGELOG.md` | Versioned changes to the protocol/config |
| `CHECKSUMS.md` | MD5 hashes of all frozen artefacts per milestone |

## Repository structure

```
RTAS/
├── 01_README/          ← governance (this folder)
├── 02_FIGURES/         ← 7 main + 4 supplementary figures (PDF + PNG)
│   ├── main/
│   └── supplementary/
├── 03_CODE/            ← reproducible analysis scripts (01–10)
└── 04_MANUSCRIPT/      ← manuscript draft (Markdown)
```

## Key numbers (v1.0-cand.5 frozen)

| Number | What it is |
|--------|------------|
| 3,714 | Innovation-training projects |
| 56,901 | OpenAlex papers (WHU, article type, 2020–2024) |
| 60,615 | Joint corpus for BERTopic (= 3,714 + 56,901) |
| 33,312 | Matched papers (58.5% of 56,901) |
| 886 | BERTopic non-outlier topics (+ 1 OUTLIER = 887 CSV rows) |

Note: "12,000" = old incomplete first-batch pool (superseded). "35,721" = label frequency sum (NOT a paper count).

## Golden rules

1. Figures in `02_FIGURES/` = outputs of `03_CODE/` only. Never hand-edit.
2. Every script in `03_CODE/` reads frozen CSVs from the private data store; never hardcode stats.
3. Never hand-edit numbers in the manuscript. If a number does not match, the frozen CSV wins.
4. `01_DATA/raw_private/` (in the private repo) = read-only archival.
5. Every freeze milestone bumps protocol version + tags Git + regenerates CHECKSUMS.
