# RTAS: Research-Training Alignment Score

Public reproducibility repository for the RTAS study on semantic alignment between
Wuhan University innovation-training project titles and OpenAlex paper titles (2020–2024).

## What this repo contains

| Folder | Content |
|--------|---------|
| `01_README/` | Governance: protocol, config snapshot, changelog, checksums |
| `02_FIGURES/` | 12 main figures + 1 supplementary figure (PDF + PNG) |
| `03_CODE/` | Reproducible analysis scripts (01–10) + R script (09) |
| `04_MANUSCRIPT/` | Manuscript draft (Markdown) |

## What this repo does NOT contain

- **Raw data** (56,901 OpenAlex papers, 3,714 project titles) — stored privately
- **Embedding vectors** (`.npy` files, 80–90 MB each) — regenerable from `03_CODE/03_embedding_models.py`
- **Author-to-college lookup** (PII) — stored privately
- **Interim CSVs** — regenerable from `03_CODE/`

## Key numbers

| Number | What it is |
|--------|------------|
| 3,714 | Innovation-training projects |
| 56,901 | OpenAlex papers (WHU, article type, 2020–2024) |
| 60,615 | Joint corpus for BERTopic (= 3,714 + 56,901) |
| 33,312 | Matched papers (58.5% of 56,901) |
| 886 | BERTopic non-outlier topics (+ 1 OUTLIER = 887 CSV rows) |

Note: "12,000" = old incomplete first-batch pool (superseded). "35,721" = label frequency sum (NOT a paper count).

## Quick start

```bash
# Install dependencies
pip install pandas numpy matplotlib scipy statsmodels sentence-transformers bertopic

# Generate all figures from frozen CSVs (requires data access)
python 03_CODE/10_generate_figures.py
```

## Key results (v0.9.1, frozen)

- 3,714 projects x 56,901 papers; K=886 BERTopic topics + 1 OUTLIER
- ANOVA F(2,3711)=35.72, p=4.3e-16; Tukey HSD: U<P<=N (P-N p-adj=0.082 ns)
- HLM: advisor_recent_3y_works_mean beta=+0.0085, p=4.5e-7 *** (sole clean predictor)
- Diffusion lag: HRLT n=24, median +0.5 yr (research leads training)
- Matthew effect: Gini=0.767, Top-5% share=34.0%, OR(top5%)=6.085

## Milestones

| Version | Status |
|---------|--------|
| v0.1 | MiniLM x 5 RTAS variants experiment — done |
| v0.2 | RTAS frozen (model/data/window/aggregation) — done |
| v0.9 | All 6 downstream analyses + manuscript + figures — done |
| v1.0 | Scientometrics submission + Zenodo DOI — pending |

## License

CC BY-NC-SA 4.0 (code); figures/data under project protocol (see `01_README/`)
