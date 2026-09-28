> **HISTORICAL v0.2 FREEZE RECORD — NOT THE CURRENT NUMERICAL SOURCE OF TRUTH.**  
> This document is retained for provenance and contains superseded first-batch/pre-audit values (for example, 12,000-paper development-stage statistics). For current post-audit manuscript values, use `../06_RESULTS/19_numerical_provenance_ledger.csv`, `../manuscript/data_verification.tex`, and the root `README.md`.

# FINAL ANALYSIS PROTOCOL — RTAS Project
**Version**: v0.2 (RTAS frozen)  |  **Date**: 2026-09-03  |  **Status**: FROZEN — DO NOT RE-OPEN WITHOUT FORMAL CHANGELIST.

> 本文件是整个论文的数据和算法"总开关"。正文、表格、图片中的所有数字都必须能追溯到本文件列出的某一行。
> 任何对本文件的修改都必须先记录在 CHANGELOG.md，并同时递增协议版本号。

---

## 1. DATA SAMPLE FREEZE

### 1.1 ITTP (Projects)

| Item             | Value                              | Source File |
|------------------|------------------------------------|-------------|
| Sample size      | **N = 3,714**                      | `01_DATA/final_analysis/table5_project_dataset_n3714.csv` |
| Years            | 2020 – 2024 (project application year) | `year` column |
| Colleges (raw)   | **40** distinct                    | `college` column |
| Colleges (HLM)   | **39** used in HLM substrate       | 1 college has no matched-author papers in the 12K-paper first batch; it has 0-row R_c(t) → dropped (see §2.3) |
| Unique supervisors | **1,940** distinct               | `supervisor_id` column (post dedup) |
| Direct supervisors | **1,899 direct** reported in old docs → replaced by 1,940 | 1,899 is from early dataset; **1,940 is canonical** (see §7) |
| Exclusion rule   | 173 projects from 8 colleges with no matched-author paper topics in the original topic-based substrate → still excluded from all analyses that use RTAS (3,714 = 3,887 − 173) | Canonical. |

### 1.2 OpenAlex Publications

| Item              | Value                              | Source File |
|-------------------|------------------------------------|-------------|
| **Unique papers** | **N = 12,000** (full corpus, all on disk) | `01_DATA/raw_private/武汉大学_OpenAlex论文逐篇数据_2020_2024_首批.csv` |
| Topic freq sum    | 35,721 cumulative topic assignments (avg 2.98 topics/paper) | Same file, `topics` column expanded |
| Matched to college| 64.5 % = 7,740 / 12,000           | `02_RTAS_MODEL_SELECTION/paper_college_year_map.csv` col `has_matched` |
| Colleges covered  | 39 of 40 (see §1.1)                | |
| Avg colleges/paper matched | 1.83                      | Precise full-name pinyin match, homonym collisions skipped |
| **Note**          | Paper text available: **title only** (no abstract); therefore RTAS is title↔title cosine. Fulltext robustness is therefore N/A and cannot be claimed in the paper. | |

### 1.3 Year Window

- **Correction** to the earlier "5-year contemporaneous window" claim in the paper draft:
  **No pre-2020 OpenAlex data exists on disk.** The window actually used is
  **cumulative `[2020, project_year]`**. Formally:
  for a project in college `c` with year `t`, its reference paper set is
  ```
  R_c(t) = { papers matched to college c | 2020 ≤ publication_year ≤ t }
  ```
  All RTAS variants, all heterogeneity analyses, and dynamic diffusion lags use this definition.
- **Honest limitation** to write in the paper: "OpenAlex corpus available to this study begins in 2020, so we use a cumulative reference window rather than a fixed-length rolling 5-year lookback. Results should be interpreted as alignment to the college's cumulative research output since 2020."

---

## 2. RTAS FREEZE (v0.2 milestone)

### 2.1 Embedding Models

| Model       | Version / HG repo             | Used as                  | Encode source | Status |
|-------------|-------------------------------|--------------------------|---------------|--------|
| **MiniLM**  | `sentence-transformers/all-MiniLM-L6-v2` | **PRIMARY embedding**    | title only    | ✅ encoded on disk |
| BGE-M3      | `BAAI/bge-m3`                 | Robustness / sensitivity | title only    | ⚠️ Deferred — torch DLL initialization unstable on this machine; re-encode in a stable env when possible, then add a new C5 inter-model column and re-run step5. |

### 2.2 RTAS Algorithm — Primary RTAS

- **Primary RTAS variable name**: `rtas_mini_mean`
- **Definition** (formal, matches paper Methods section):

  Let `p_i` be the L2-normalized MiniLM embedding of the **title** of project `i`,
  `C(i)` be its college, `t(i)` its project year.
  Let `q_j` be the L2-normalized MiniLM embedding of the **title** of paper `j`,
  and `R_{C(i)}(t(i))` be the college-year paper set (§1.3).

  ```
  RTAS_i  =  mean_{ j ∈ R_{C(i)}(t(i)) }  [ q_j · p_i ]
  ```

  i.e. **arithmetic mean cosine similarity between the project title embedding and each paper-title embedding in the college-year set.**

- **NOT used**: Top-5, Top-10, Top-20, centroid variants → downgraded to sensitivity analysis
  (see §2.4). The flowchart in the paper must therefore say "Mean cosine over college-year paper set"
  and **NOT** "Top-5 cosine similarity".

### 2.3 Missing / Undefined Cases

- A project's RTAS is **NaN** if `|R_{C(i)}(t(i))| == 0` (college with 0 matched papers up to year t).
  There is exactly **1** such project in the 3,714 sample.
- HLM / ANOVA / correlations drop this single NaN row automatically.
- This explains the **40 vs 39 college difference** in §1.1: the 40th college has no matched-author paper
  in the 12K first-batch, so it has all-NaN RTAS and is silently dropped by `lme4` / `statsmodels`
  (hence HLM reports 39 groups). The primary 3,714 project set still references 40 colleges
  (`college` column), but 1 of 40 contributes no RTAS variation.

### 2.4 Model Selection — Pre-Specified Rule Applied Verbatim

| Criterion | Rule                                                                 |
|-----------|----------------------------------------------------------------------|
| C1        | Construct validity: Spearman( RTAS, human 150-pair relevance labels ). Threshold ≥0.15. |
| C2        | Known-groups validity: ANOVA η² of RTAS across project level (national / provincial / university-level). Require C2_p < 0.05 for shortlist. |
| C3        | K-stability: Spearman rank correlation of Top-5 vs Top-10 vs Top-20 ranking (title-only env → repurposed from "title vs fulltext robustness"). |
| C4        | Stability: (a) year-normalized SD of mean RTAS (lower = more stable); (b) college-level ICC via mixed LM (singular fit → NaN, proxied by year SD). |
| C5        | Convergent validity: Spearman( new RTAS, original topic-based rtas_sbert ). Replaced by MiniLM↔BGE inter-model Spearman once BGE is encoded. |

**Aggregation shortlist rule**: within the chosen embedding, keep only C2_p < 0.05 (all 5 variants pass),
then rank by the composite `0.45 · η²_norm + 0.30 · stability_norm + 0.25 · C3_norm`.
Top-K preference tie-break: a Top-K variant is preferred if within 5% of the top composite (not triggered; mean is +55% above top5).

### 2.5 Selection Results

| Variant          | C1 human | C2 η²  | C3 K-stab | C4 year SD | C5 convergent | Composite |
|------------------|----------|--------|-----------|------------|---------------|-----------|
| **mean (PRIMARY)** | 0.405 | **0.0175** | 0.991   | 0.101      | 0.362         | **0.742** |
| top5             | 0.405    | 0.0154 | 0.991     | 0.109      | 0.396         | 0.480     |
| top10            | 0.405    | 0.0162 | 0.991     | 0.128      | 0.386         | 0.447     |
| top20            | 0.405    | 0.0170 | 0.991     | 0.153      | 0.362         | 0.398     |
| centroid         | 0.405    | 0.0133 | 0.991     | 0.099      | 0.378         | 0.300     |

Full table: `02_RTAS_MODEL_SELECTION/rtas_model_selection.csv`.
Decision log: `02_RTAS_MODEL_SELECTION/selection_report.md`.
Machine-readable decision: `02_RTAS_MODEL_SELECTION/PRIMARY_RTAS.json`.

### 2.6 Primary RTAS Distribution

| Statistic | Value   |
|-----------|---------|
| n_valid   | 3,713   |
| min       | −0.083  |
| max       | 0.376   |
| mean      | 0.1329  |
| sd        | 0.0779  |

MiniLM cosine can legitimately be slightly negative (embeddings are not non-negative).
This is expected and not an error.

---

## 3. DOWNSTREAM ANALYSIS PIPELINE (待阶段三冻结)

All analyses below MUST use `rtas_mini_mean` as the sole primary RTAS variable.
Other variants and BGE-M3 enter only as sensitivity / robustness tables in the Supplement.

| Stage | Analysis                 | Output location                 | Status          |
|-------|--------------------------|---------------------------------|-----------------|
| 3.1   | Static BERTopic / 4-Quadrant | `03_FINAL_ANALYSIS/topic_model/` | Pending (use same 2,449 K as original docs for comparability; regenerate with primary RTAS cut) |
| 3.2   | RTAS heterogeneity — project level | `03_FINAL_ANALYSIS/heterogeneity/` | Pending (national > provincial > university-level) |
| 3.3   | RTAS heterogeneity — college  | `03_FINAL_ANALYSIS/heterogeneity/` | Pending (Top 20 college RTAS; use 10pt college names per chart policy) |
| 3.4   | Hierarchical Linear Model (RQ3) | `03_FINAL_ANALYSIS/hlm/`     | Pending — MUST produce Table and Forest Plot from the SAME fitted model object. Table 6 HLM and Fig 6 Forest Plot in current draft are NOT aligned. |
| 3.5   | Gini + transition + logistic (RQ4, Matthew effect) | `03_FINAL_ANALYSIS/matthew_effect/` | Pending |
| 3.6   | Dynamic Diffusion Lag    | `03_FINAL_ANALYSIS/diffusion_lag/` | Pending. Definition: `t_project − t_paper` where `t_paper = first year topic > 1.5% in papers`, `t_project = first year topic > 0.5% in projects`. |
| 3.7   | RI-CLPM longitudinal     | `03_FINAL_ANALYSIS/ri_clpm/`    | Pending. Supervisor×year panel with `papers_count, citations_mean, srtp_count, srtp_rtas_mean`. Language: "cross-lagged / longitudinal directional evidence", NOT strict causality. |

---

## 4. FIGURES AND TABLES PROVENANCE RULES

**Hard rules, enforced by the repository structure:**

1. Everything in `04_FINAL_TABLES/` and `05_FINAL_FIGURES/` must be produced by a script in `06_CODE/` reading from `01_DATA/final_analysis/` or an analysis output in `03_FINAL_ANALYSIS/`.
2. **No manual copy-paste of historical figures** from `D:\dachuang_outputs\…` or the old `SCI_最终投稿图表包` into `05_FINAL_FIGURES/`.
3. If a historical figure is to be kept, re-implement its plotting pipeline in `06_CODE/10_generate_figures.py` (or a dedicated module) and regenerate it against the frozen analysis CSVs.
4. Every final figure and table must have a 1-line provenance comment in the generator script:
   ```python
   # Figure 6 HLM Forest Plot  <--  03_FINAL_ANALYSIS/hlm/final_hlm_fit.feather  --(06_CODE/07_hlm.py)-->  05_FINAL_FIGURES/main/Figure6_HLM_Forest.pdf
   ```
5. Figure titles must be in English, no "Fig1 / 图2" inside the image canvas. (Chart policy from user preferences.)
6. All figures saved as PDF (vector, preferred) **or** 600 dpi PNG into `05_FINAL_FIGURES/`.
7. MD5 hashes of final figures and tables are recorded in `00_README/CHECKSUMS.md` after each freeze milestone.

---

## 5. RANDOMNESS AND REPRODUCIBILITY

| Item                | Value |
|---------------------|-------|
| Global random seed  | **42** (numpy, pandas.sample, sklearn, BERTopic, python.random) |
| BERTopic seed       | `umap.random_state=42`, `hdbscan` not seeded directly but deterministically reproducible with identical input and same UMAP params |
| Train/test splits   | Not applicable in this observational study; any sampling uses `random_state=42` |
| LLM validation prompt temperature | 0, max_tokens=2 |

---

## 6. ETHICS, PRIVACY, AND DATA SHARING

- `01_DATA/raw_private/` and fields carrying student name / supervisor name / precise college identifiers in `final_analysis/` must never leave the local machine and must never appear in the GitHub public repo.
- The public GitHub repo (`RTAS-knowledge-diffusion`) only ships:
  - `data/example/` synthetic or 5% sampled, fully de-identified snippet
  - aggregate-level results tables (e.g. college RTAS means with college relabeled as "C01…C40")
- Full final dataset (including private identifiers) is archived on this machine and optionally mirrored to Zenodo as a "restricted-access" record if requested; the GitHub repo links to a Zenodo archive of the code-only snapshot.

---

## 7. REPLACEMENT OF OUTDATED VALUES (CANONICAL NUMBER LIST)

All numbers below supersede any earlier figure in the paper draft. Search-and-replace list:

| Old value in draft         | Canonical replacement    | Where                                        |
|----------------------------|--------------------------|----------------------------------------------|
| N = 7,356                  | **学生总人次** (if at all mentioned) OR remove | Do not use as project count. |
| 导师数 1,899               | **1,940 unique supervisors** (1,926 valid after HLM-level exclusion) | Abstract / Methods / Descriptive Table |
| 学院数 39                  | **40 total; 39 in HLM substrate** (1 college has 0 matched-author papers → all-NaN RTAS, dropped) | Methods / HLM section |
| Top5%导师数 94             | **97**                                   | Matthew effect section (1,940 × 5%) |
| Gini coefficient 0.744     | **0.767**                                | Matthew effect section |
| Top5% 国家级项目占比 30.4% | **34.0%**                                | Matthew effect section |
| ANOVA: `F(38, 3674)`       | **F(38, 3674)**                          | College heterogeneity ANOVA (within df = 3,713 non-NaN RTAS rows − 39 groups in substrate, NOT 3,714−39 = 3,675) |
| "5-year paper window" phrasing | **cumulative [2020, project_year] window** | Methods §RTAS, Limitations |
| "Top-5 cosine" in flowchart | **Mean cosine over college-year paper set** | Fig2 / methods flowchart |
| RTAS human Spearman 0.098  | Cite 0.098 as **OLD topic-based RTAS validity**; new **paper-based Primary RTAS** reports **C1 = 0.405** (150 pairs) | RTAS Validation section. Spearman 0.56 is **inter-rater reliability of human annotators**, NOT RTAS validity. |

Full old→new audit: see `D:\vc-task\complete_verification.csv` (stored in working dir; mirrored to `08_ARCHIVE/` if needed).

---

## 8. VERSIONING AND MILESTONES

Git tags on the **GitHub public repo** and equivalent folder snapshots in `08_ARCHIVE/`:

| Milestone       | Tag    | Description                                      |
|-----------------|--------|--------------------------------------------------|
| Model-selection experiments | v0.1 | MiniLM × 5 RTAS variants experiment runs        |
| **RTAS frozen** | **v0.2** | ✅ THIS DOCUMENT. Primary RTAS = `rtas_mini_mean`. Data sample and windows frozen. |
| Analysis freeze | v0.9   | BERTopic / HLM / Matthew / Diffusion / RI-CLPM all regenerated with Primary RTAS and signed off. |
| Submission      | v1.0   | Scientometrics submission snapshot (figures, tables, manuscript). Zenodo DOI minted. |

Any change to §1, §2, or §7 after v0.2 requires a changelist in `CHANGELOG.md` and a bump to v0.3.
