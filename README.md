# RTAS: Research–Training Alignment Score

Public reproducibility repository for the study:

> **Linking Undergraduate Innovation and Entrepreneurship Training Projects to
> Institutional Publication Portfolios: A Cross-Lingual Measure of
> Research–Training Alignment**

RTAS is the mean cosine similarity between a student project-title embedding and
the unique OpenAlex articles assigned to the same academic unit through
advisor–author linkage. Project titles are predominantly Chinese whereas nearly
all indexed article titles contain no Chinese characters, so the measure relies
on cross-lingual sentence embeddings
(`paraphrase-multilingual-MiniLM-L12-v2`). RTAS indexes semantic alignment, not
training quality; all estimates are observational.

A compiled snapshot of the manuscript is in `manuscript/preview/`.

## Repository map

| Folder | Content |
|--------|---------|
| `01_README/` | Governance: analysis protocol, frozen config, changelog, checksums |
| `02_FIGURES/` | Full engineering figure set — 9 main (incl. standalone 8a/8b panels) + 5 supplementary, PDF + PNG, engineering file names |
| `03_CODE/` | Reproducible analysis scripts 01–22 (09 in R), incl. the figure generator `10_generate_figures.py` |
| `05_VALIDATION/` | Validity-program artefacts: 150-pair rating files, rater-agreement statistics, lexical baselines, BGE-M3 benchmark |
| `06_RESULTS/` | Frozen aggregate outputs (counts and coefficients only) + the 115-check numerical provenance ledger |
| `manuscript/figures/` | The 12 submission figures named as in the paper (7 main + S1–S4), PDF + PNG |
| `manuscript/preview/` | Compiled paper snapshots (latest: `RTAS_final_package_2026-09-23.pdf`) |
| `manuscript/data_verification.tex` | Ready-to-insert blocks for the manuscript master: the "Data verification and numerical provenance" subsection and supplement Tables S3–S4 |
| `archive/internal_history/` | Superseded working drafts (provenance only; not part of the submission) |

The LaTeX master of the manuscript is maintained on Overleaf; this repository
mirrors the submission figure set, the compiled snapshot, and the verification
fragment.

## What this repo does NOT contain

- **Raw data** (56,901 OpenAlex records, the 3,714-project registry, the author-to-college lookup with personal information) — stored privately
- **Embedding vectors** (`.npy`, 80–90 MB each; regenerable via `03_CODE/03_embedding_models.py`)
- **Interim CSVs** — regenerable from `03_CODE/`

## Key numbers (post-freeze; independently verified, 115/115 PASS)

| Number | What it is |
|--------|------------|
| 3,714 | UIETP projects, 2020–2024 (1,375 university / 1,657 provincial / 682 national; innovation-training + entrepreneurship-training tracks) |
| 56,901 | OpenAlex articles (WHU, type=article, 2020–2024); +22,438 from 2017–2019 used only for pre-project advisor covariates |
| 33,312 (58.5%) | Articles advisor-matched to academic units; these form the RTAS reference portfolios |
| 60,615 | Joint BERTopic corpus (56,901 + 3,714 titles) → 886 non-outlier topics |
| 5 / 173 / 10 / 698 | Quadrant topic counts: HRHT / HRLT / LRHT / LRLT |
| 29 (24 HRLT + 5 HRHT) | Topics with definable diffusion lags; HRLT median lag +0.5 years |
| 0.1212 / 0.1391 / 0.1460 | Mean RTAS by administrative project tier (university / provincial / national); F(2,3711)=35.72, η²=1.89% |
| ICC = 0.7376 | Two-level random-intercept mixed model (3,231 complete cases, 39 units) |
| +0.0043 / −0.0063 | Advisor pre-project publications (3 y) / prior supervisory load (both p < 0.001) |
| Gini = 0.746; top-5% share = 31.0% | National-project concentration across 1,834 advisors |
| OR = 2.06 [1.53, 2.76] | Lagged national-project persistence (2.45 [1.91, 3.16] under the full-grid risk set) |
| ρ = 0.405; AUC = 0.880 | Embedding-level pairwise validity (150 pairs) |

Note: "12,000" = superseded first-batch development pool (aggregation selection
only); "35,721" = label-frequency sum, not a paper count.

## Quick start

```bash
# Install dependencies
pip install pandas numpy matplotlib scipy statsmodels sentence-transformers bertopic

# Regenerate all figures from the frozen CSVs (requires private data access)
python 03_CODE/10_generate_figures.py
```

## Milestones

| Version | Status |
|---------|--------|
| v0.1–v0.2 | MiniLM variant experiments; RTAS frozen (model / data / window / aggregation) — done |
| v0.9 | Downstream analyses + manuscript + figures — done |
| v1.0-cand.5–7 | Figure-freeze iterations; manuscript text freeze — done |
| v1.1-postaudit | Numerical provenance audit (115/115 PASS), registry re-verification, exclude-2022 sensitivity (Table S2), final figure labels synced to manuscript terminology, monochrome S1, manuscript master on Overleaf — done |
| v1.0 | Journal submission; repository goes public — pending |

## License

CC BY-NC-SA 4.0 (code); figures/data under the project protocol (see `01_README/`).
