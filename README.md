# RTAS: Research-Training Alignment Score

Public reproducibility repository for the RTAS study on semantic alignment between
Wuhan University innovation-training project titles and OpenAlex paper titles (2020–2024).

## What this repo contains

| Folder | Content |
|--------|---------|
| `00_README/` | Governance: protocol, config snapshot, changelog, checksums |
| `06_CODE/` | Reproducible analysis scripts (01–10) + R script (09) |
| `05_FINAL_FIGURES/` | 12 main figures + 1 supplementary figure (PDF + PNG) |
| `07_MANUSCRIPT/` | Manuscript draft (Markdown) |

## What this repo does NOT contain

- **Raw data** (56,901 OpenAlex papers, 3,714 project titles) — stored privately
- **Embedding vectors** (`.npy` files, 80–90 MB each) — regenerable from `06_CODE/03_embedding_models.py`
- **Author-to-college lookup** (PII) — stored privately
- **Interim CSVs** — regenerable from `06_CODE/`

## Quick start

```bash
# Install dependencies
pip install pandas numpy matplotlib scipy statsmodels sentence-transformers bertopic

# Generate all figures from frozen CSVs (requires data access)
python 06_CODE/10_generate_figures.py
```

## Key results (v0.9.1, frozen)

- 3,714 projects × 56,901 papers; K=886 BERTopic topics + 1 OUTLIER
- ANOVA F(2,3711)=35.72, p=4.3e-16; Tukey HSD: U<P≤N (P-N p-adj=0.082 ns)
- HLM: advisor_recent_3y_works_mean β=+0.0085, p=4.5e-7 *** (sole clean predictor)
- Diffusion lag: HRLT n=24, median +0.5 yr (research leads training)
- Matthew effect: Gini=0.767, Top-5% share=34.0%

## License

CC BY-NC-SA 4.0 (code); figures/data under project protocol (see `00_README/`)
