# RTAS_FINAL_PROJECT — Private Research Repo (NOT for GitHub)

> **Two-repository principle**: this folder is the complete private working repo for the
> "Research-Training Alignment Score" paper. It contains raw PII-bearing data,
> historical experiments, and all manuscript sources. The companion **GitHub public
> repo** (`RTAS-knowledge-diffusion`) contains ONLY the cleaned reproducibility code,
> a final config snapshot, example data, and docs — never raw records.

```
RTAS_FINAL_PROJECT/
│
├── 00_README/                  ← YOU ARE HERE; this repo's governance files
│   ├── README.md                  this file
│   ├── FINAL_ANALYSIS_PROTOCOL.md v0.2+ SINGLE SOURCE OF TRUTH for sample, RTAS, pipeline
│   ├── final_config.yaml          machine-readable parameter sheet (v0.2+)
│   ├── CHANGELOG.md               versioned changes to the protocol/config
│   └── CHECKSUMS.md               MD5 hashes of all frozen artefacts per milestone
│
├── 01_DATA/
│   ├── raw_private/           ← untouched originals, never on GitHub, never edit
│   ├── interim/               ← paper→college maps, author lookups, intermediate CSVs
│   ├── final_analysis/        ← CANONICAL ANALYSIS INPUTS (only CSVs scripts read)
│   └── public_sample/         ← 5% sampled / de-identified snippet for GitHub
│
├── 02_RTAS_MODEL_SELECTION/  ← v0.2 milestone: MiniLM × 5 variants evaluated
│   ├── embeddings/{minilm,bge_m3}/
│   ├── human_validation/        150-pair human annotations (C1 input)
│   ├── 01_… → 06_*.py           reproduce paper→college map, encode, compute variants, evaluate, select, verify
│   ├── rtas_model_selection.csv final 5-criteria table (5 MiniLM rows, 5 BGE rows TBD)
│   ├── PRIMARY_RTAS.json        machine-readable decision
│   └── selection_report.md      narrative decision log
│
├── 03_FINAL_ANALYSIS/         ← ONE SUBFOLDER PER ANALYSIS STAGE
│   ├── topic_model/           BERTopic K=2449-ish + 4-quadrant cuts
│   ├── heterogeneity/         project-level ANOVA / college ANOVA / top-20 ranking
│   ├── hlm/                   lme4 / linearmodels HLM fit → produce TABLE & FOREST from SAME object
│   ├── matthew_effect/        Gini + transition matrix + logistic + Top5% t-tests
│   ├── diffusion_lag/         Dynamic BERTopic + topic lag t_project − t_paper
│   └── ri_clpm/               Supervisor×year panel → RI-CLPM directional evidence
│
├── 04_FINAL_TABLES/          ← ONLY tables generated from 03_FINAL_ANALYSIS by 06_CODE
├── 05_FINAL_FIGURES/         ← ONLY figures generated from 03_FINAL_ANALYSIS by 06_CODE
│   └── main/ supplementary/    (chart policy enforced in final_config.yaml §6)
│
├── 06_CODE/                  ← PURE, REPRODUCIBLE SCRIPTS
│   │                            Read final_config.yaml + 01_DATA/final_analysis;
│   │                            Write 03_FINAL_ANALYSIS/ CSVs, 04_FINAL_TABLES, 05_FINAL_FIGURES.
│   │                            Every script carries a PROVENANCE comment per output.
│   ├── 01_data_cleaning.py
│   ├── 02_author_matching.py
│   ├── 03_embedding_models.py
│   ├── 04_rtas_selection.py
│   ├── 05_topic_model.py
│   ├── 06_diffusion_lag.py
│   ├── 07_hlm.py
│   ├── 08_matthew_effect.py
│   ├── 09_ri_clpm.R
│   └── 10_generate_figures.py
│
├── 07_MANUSCRIPT/            ← LaTeX sources for the paper
│   ├── main.tex / references.bib
│   ├── figures/ tables/        symlinked or copied from 04/05 at freeze time
│   └── supplementary.tex
│
├── 08_ARCHIVE/               ← frozen milestone snapshots
│   └── frozen_release_v0.2/     copy of v0.2 artefacts
│
└── _helpers/                 ← admin scripts (checksums, validation, not science)
    └── _gen_checksums.py
```

## Golden Rules (enforced; violations require CHANGELOG entry)

1. **`04_FINAL_TABLES/` + `05_FINAL_FIGURES/` = outputs of `06_CODE/` only.**
   Never copy-paste a historical figure or table from `D:\dachuang_outputs\…` into them.
   If a historical figure is to be reused, re-implement its pipeline in `06_CODE/` against
   the frozen CSVs in `01_DATA/final_analysis/` + `03_FINAL_ANALYSIS/`.
2. **Never hand-edit numbers in the manuscript.** If a number in `main.tex` does not match
   `final_config.yaml §7 canonical_numbers` or a CSV in `03_FINAL_ANALYSIS/`, the CSV wins.
3. **Every freeze milestone bumps protocol version + tags Git + regenerates CHECKSUMS.**
4. **`01_DATA/raw_private/` = read-only archival.** Any transformation outputs go to
   `01_DATA/interim/` first, and only the vetted canonical CSVs are promoted into
   `01_DATA/final_analysis/`.

## Milestones / Versioning

| Tag       | What is frozen                               | Status   |
|-----------|----------------------------------------------|----------|
| v0.1      | MiniLM × 5 RTAS variants experiment run     | done     |
| **v0.2**  | **RTAS frozen.** Data sample, year-window, embedding, aggregation chosen (PRIMARY: `rtas_mini_mean`). Outdated canonical numbers list signed off. | ✅ **CURRENT** |
| v0.9      | All 6 downstream analyses regenerated with primary RTAS and HLM table↔figure aligned | pending  |
| v1.0      | Scientometrics submission. Zenodo DOI for code snapshot minted. | pending  |

## Do NOT push this directory to GitHub

Use the sibling folder `D:\vc-task\RTAS\` (the clean public reproducibility repo) for
anything intended to go to GitHub.com. See `RTAS/README.md` for what goes there.

## Quickstart (after v0.2)

```powershell
cd D:\vc-task\RTAS_FINAL_PROJECT
# Verify frozen artefacts are intact:
python _helpers\_gen_checksums.py
# Then begin analyses in order:
python 06_CODE\05_topic_model.py
python 06_CODE\06_diffusion_lag.py
python 06_CODE\07_hlm.py
python 06_CODE\08_matthew_effect.py
# (Rscript)  06_CODE\09_ri_clpm.R
python 06_CODE\10_generate_figures.py
```
