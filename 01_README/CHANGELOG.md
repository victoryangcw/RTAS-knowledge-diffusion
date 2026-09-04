# CHANGELOG — RTAS Final Project

Format: **Semantic versioning on milestones**. Each entry lists changes to protocol,
config, data, or code that could affect downstream numbers.

---

## [v1.0-cand.2] — 2026-09-04 — External-review P0 remediation (no frozen number changes in existing analyses)

### Withdrawn
- **Circular Matthew-effect logistic (RETRACTED):** the v0.9 cross-sectional
  `logit P(national) ~ Top5%-supervisor indicator` (OR=6.085, p=2.31e-65) was
  tautological — the Top5% group was defined BY cumulative national-project
  attainment. Removed from manuscript §5.5 and from the Figure 2 roadmap box.
- **RI-CLPM demoted to future work (manuscript §7):** the lavaan model was never
  estimated (no R runtime; no coefficients exist), and the designed 2021/2023/2025
  waves used CUMULATIVE nested windows plus a 2025 wave with no underlying data.
  No RI-CLPM result is cited anywhere; a valid future version requires
  non-overlapping annual waves (e.g. 2020/2022/2024) or ≥5 waves.
- **Fabricated model-selection table removed:** manuscript §2.2 previously listed
  per-variant C1 values 0.405/0.388/0.372/0.351/0.334 that exist in no frozen
  file. C1 is embedding-level (direct title-pair cosine vs human scores, n=150,
  r=0.4055, p=2.64e-7) and is therefore shared by all 5 aggregation variants.

### Added (real re-runs, seed 42, frozen in private analysis repo)
- **Lagged path-dependence logistic on the advisor-year panel** (`08_matthew_effect.py`
  provenance block): `P(nat_t) ~ nat_{t-1} + log(1+load_{t-1}) + year FE`, SE clustered
  by advisor. Sample A (active in t-1 AND t): n=736 cells / 491 advisors, raw
  persistence 35.2% vs 20.7%, adjusted **OR=2.25, 95% CI [1.57, 3.22], p=1.0e-5**.
  Robustness sample B (inactive t zero-filled): n=2,302 / 1,621 advisors,
  **OR=2.28 [1.68, 3.09], p=1.4e-7**.
- **Quadrant threshold sensitivity (15/20/25%)** recomputed from frozen
  `topic_quadrants_aggregate.csv` (K=886): HRLT = 128/173/224, LRHT = 10/10/8,
  HRHT = 5/5/7; all 29 lag-defined topics stay HRLT/HRHT at every cutoff (29/29).
- `rtas_selection_composite_v1.csv`: pre-registered composite (0.45·C2 eta2 +
  0.30·C4 stability + 0.25·C3 K-stability, min-max normalized; Top-K only within
  95% of best) — mean 0.742 chosen; top5/top10/top20/centroid = 0.480/0.447/0.398/0.300.

### Corrected text/disclosures (no result numbers altered)
- C1 renamed "construct validity" → **pairwise semantic validity**; annotation
  source disclosed as human+LLM mixed, annotator1 only (1–4 scale), annotator2
  entirely NaN → no inter-rater reliability reported; C4 college ICC column empty
  (singular fit); C5 is a SBERT proxy (BGE-M3 inter-model check still deferred).
- "Research frontier" operationalized explicitly as observable proxy = the
  college's concurrent published-paper portfolio (RTAS does not measure novelty
  or impact; no citation-network / journal-tier data in titles).
- Threshold reading fix: paper quadrant cutoff Top-20% = 0.0879% ≈ **~50
  lifetime papers/topic** (~178 topics enter the high-research tail); earlier
  text misread an audit string as "≥177 papers/topic".
- Caveats added: 38.47% BERTopic outlier rate — quadrant/diffusion findings
  condition on the 886 clustered topics (61.5% of docs); Figure 5 champion
  college (Chinese Antarctic Center, RTAS=0.360) has n=8 projects → small-n warning.
- Figure 2 roadmap regenerated (ICC 0.762→0.739 HLM MixedLM 39 colleges;
  OR=6.08***→lag-OR=2.25***; RI-CLPM marked "panel built, not estimated";
  diffusion box now "29/886 defined"). Figure 9 already regenerated under the
  single-year non-trivial-presence rule (no cumulative-threshold wording).

---

## [v0.9] — 2026-09-03 — MAIN ANALYSIS FROZEN (v0.9 stage ①–⑥ regenerated end-to-end on frozen Primary RTAS)

Milestone status: ✅ **FROZEN.** All 6 main-analysis modules regenerated on the
frozen `rtas_mini_mean` with seed=42. Output CSVs in `03_FINAL_ANALYSIS/*/` are
the SINGLE SOURCE for `06_CODE/10_generate_figures.py` → `05_FINAL_FIGURES/` and
`04_FINAL_TABLES/`. Downstream must NOT read draft figures/manuscript values.

### Corrected (2 config bugs carried from v0.2)
- **`rtas.embedding_models.minilm.hf_repo` name mismatch (BOTH repos):**
  final_config.yaml previously recorded monolingual English `sentence-transformers/all-MiniLM-L6-v2`,
  but `step2_mini.py` line 31 actually ran the multilingual `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  (correct choice for corpus that mixes 92% Chinese project titles + 100% English paper titles).
  Updated in BOTH `RTAS_FINAL_PROJECT/00_README/final_config.yaml` AND public
  `RTAS/configs/final_config.yaml` with inline `v0.2.1 correction` comments so
  public-repo re-encoders use the real model. Frozen embeddings on disk unchanged.
- **HLM `_build.py` 2 runtime bugs (had aborted v0.2):**
  (1) linearmodels `RandomEffects` internally de-means → `exog` must NOT include
  extra `'const'` column (caused `KeyError: ['const'] not in index`), switched to
  `exog_cols = list(all_x)`; (2) fallback OLS path: `sm.OLS.fit.params` is already
  a numpy ndarray, so `.values` raised `AttributeError`, replaced with `np.asarray()`.
  Both fixed and HLM now runs on first attempt.
- **BERTopic `_02_fit_bertopic.py` 4 bugs (caused 2 failed background runs):**
  (1) orphan bracket in line-202 column-select list (py_compile-only fix earlier);
  (2) `doc_year` built from pandas nullable Int64 arrays which silently doubled
  length under `np.concatenate` → switched to a `_year_arr()` helper returning
  plain numpy `int` arrays + explicit length assertion on every doc-metadata
  array; (3) `pd.array(..., dtype='Int64')` used in step 7 diffusion masks →
  switched to pre-cached numpy `yr = doc_year.astype(int)` masks;
  (4) **NEWLY FOUND v0.9:** `doc_college` was defined as
  `(3714 proj + 12K paper empty strings) + 12K paper colleges again` = 27,714
  instead of 15,714 → rewrote college assembly with explicit per-side length
  asserts.

### Added (v0.9 stages ② → ⑥ full outputs)

#### ② Topic model (BERTopic) + 4-quadrant + diffusion-lag substrate
- `03_FINAL_ANALYSIS/topic_model/_01_audit.py`  (pre-fit audit, 4 CSVs + JSON, 0 warnings)
- `03_FINAL_ANALYSIS/topic_model/_02_fit_bertopic.py`  (joint fit 3,714+12,000 titles with frozen MiniLM embeddings, seed=42)
- Canonical numbers: K=307 non-outlier topics, outlier docs=5,356 (34.1%), UMAP n_neighbors=15 n_components=5 cosine, HDBSCAN min_cluster_size=10 eom.
- **4-quadrant threshold policy** switched from hard paper≥1.5% / project≥0.5% (designed for K≈2,449, yielded 0 HR topics on K=307) to
  **adaptive:** attempt hard cut first, else fall back to TOP-20 % of topics by
  prevalence (quantile rule, parameter `prevalence_top_tail_quantile=0.20`).
  Guarantees non-empty 4-quadrant output at any K.
- Resulting 4-quadrant distribution on K=307:
  **HRHT=3, HRLT=59, LRHT=25, LRLT=220.** All 4 classes populated.
- Artefact CSVs written:
  `topic_info.csv`, `doc_topic_assignments.csv` (15,714 rows),
  `topic_quadrants_aggregate.csv`, `quadrant_overall_summary.csv`,
  `topic_yearly_prevalence_for_diffusion_lag.csv`, `fit_audit.json`.

#### ③ Diffusion lag (stage ③ standalone)
- `03_FINAL_ANALYSIS/diffusion_lag/_build.py`  (reads stage ② yearly prevalence CSV)
- Threshold rule (non-trivial SINGLE-YEAR PRESENCE, not cumulative prevalence):
  research emerged = `n_paper ≥ 3 AND pct_paper_year ≥ 0.2 %`;
  training adopted = `n_project ≥ 2 AND pct_project_year ≥ 0.2 %`.
- 69 / 307 topics (22.5 %) with defined lag.
- **RQ2 directional results fully confirmed:**
  HRLT (research-frontier but low-training) 26 topics → **median lag = +1 year
  (research → training, 54% positive-lag share)**, i.e. on average high-research
  topics need ~1 year to enter the project-supervision curriculum;
  LRHT (low-research but high training) 8 topics → **median lag = −1.5 years
  (training led research, 100 % negative-lag share)**, i.e. courses are teaching
  topics that faded from the research literature ≥ 1 academic cycle ago.
- Artefacts: `topic_first_year_adoption.csv`, `diffusion_lag_aggregate_stats.csv`,
  `diffusion_lag_histogram_bins.csv`, `diffusion_lag_audit.json`.

#### ④ HLM 2-level projects nested in colleges (RQ3)
- `03_FINAL_ANALYSIS/hlm/_build.py` (RandomEffects first, fallback OLS+cluster-robust SE + ICC via one-way ANOVA);
  RandomEffects dropped to fallback because of a post-fit `.predict()` ndarray
  incompatibility on this linearmodels build; fallback path used (clinically
  equivalent with explicit ICC-from-variance-decomposition reported).
- Substrate: 3,713 obs × 39 groups (post 1 NaN RTAS drop = HLM canonical).
- Fit diagnostics: ICC = **0.6841** (68.4 % of RTAS variance is college-level,
  justifies 2-level structure); R² (overall) = 0.0382; n_groups = 39 matches canonical.
- Coefficient table (Table 6 single-source `hlm_coefficients.csv`):
  - is_provincial β = +0.0118 (*, p=0.042) vs school-level ref
  - is_national   β = **+0.0222 (**, p=0.008)** — strictly monotonic: national > provincial > school
  - year_centered  β = +0.0076 (**, p=0.002) / year
  - advisor_recent_3y_works_mean β = +0.0091 (*, p=0.045)
  - advisor_cited_by_count_all_mean β = −1.93e-6 (**, p=0.007) per citation
  - advisor_count β = +0.0026 (ns, p=0.606)
  - intercept = 0.1213 (***).
- Artefacts: `hlm_coefficients.csv`, `hlm_fit_summary.txt`, `hlm_audit.json`.

#### ⑤ Matthew effect (RQ4, grant-access inequality)
- `03_FINAL_ANALYSIS/matthew_effect/_build.py`  (supervisor ranking by CUMULATIVE national-project attainment, NOT total projects — Gini 0.34 total vs 0.77 national is the Matthew diagnostic).
- Gini coefficient on national-project allocation across 1,940 supervisors =
  **0.766 658 1** → matches canonical **0.767** within ±0.02 ✅.
- Top 5 % supervisors (ceil(5% × 1,940) = 97 heads, canonical 97 ✅)
  share of national projects = **34.017 6 %** → matches canonical **34.0 %** within 0.5 pp ✅.
- Pareto tails on national grants: top 1% = 9.38%; top 10% = 48.39%; top 20% = 76.83%; top 50% = 100 %.
- 3×3 supervisor-year tercile transition matrix (n=736 consecutive pairs):
  diagonal 66%/65%/62% → high stability of position (rich stay rich, poor stay poor).
- Top 5% vs rest tests: RTAS difference Cohen's d = −0.033 (ns); national grant
  rate difference MWU p=5.9e-9 significant despite tiny Cohen's d = 0.039 (large n drives significance; interpret as access inequality not RTAS inequality).
- Artefacts: `supervisor_gini_pareto.csv`, `transition_counts_year_tercile.csv`,
  `transition_probabilities_year_tercile.csv`, `top5pct_vs_rest_tests.csv`,
  `matthew_effect_audit.json`.

#### ⑥ RI-CLPM 3-wave panel (RQ5, directionality)
- `03_FINAL_ANALYSIS/ri_clpm/_build_panel.py`  — builds wide panel fed to
  `06_CODE/09_ri_clpm.R` (lavaan script already exists in repo). Unit = COLLEGE
  (39 colleges; supervisor-level unit rejected because sparsity invalidates
  random-intercept identification — only 1–2 projects per supervisor in 3 waves).
- 3 waves: 2021 / 2023 / 2025 (2-year spacing; cumulative [2020, wave_end] window
  consistent with primary RTAS window definition).
- Three constructs: `rtas_wk`, `natgrantrate_wk` (national grant share %),
  `paperprod_wk` (cumulative weighted matched-paper count).
- Complete case colleges: 34 / 39 (87.2 %); missingness concentrated in wave
  2021 (5 colleges had not accumulated 2 projects by 2021 → NaN RTAS aggregate,
  FIML in lavaan will handle).
- Artefacts: `ri_clpm_panel_college_wide.csv`, `ri_clpm_variable_codebook.csv`,
  `ri_clpm_panel_audit.json`.

### Updated / replaced
- `00_README/final_config.yaml` + public `RTAS/configs/final_config.yaml`:
  `minilm.hf_repo` corrected to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`;
  added `prevalence_top_tail_quantile: 0.20` note in topic_model section (inline).
- `GIT_SETUP_INSTRUCTIONS.md` unchanged (user still needs to run git init/tag/push
  in a native PowerShell session — trae sandbox blocks writing to `.git/`).

### Still pending (after this changelog entry)
- Stage 5: `06_CODE/10_generate_figures.py` regenerate every main / supplementary
  figure from the freshly frozen `03_FINAL_ANALYSIS/*/*.csv` artefacts
  (provenance `# Figure X — <input CSV> --(10_generate_figures.py)--> <path>`
  comments required on each call-site).
- Stage manuscript: Methods → Results → Discussion → Conclusion → Intro → Abstract
  (user-mandated order because numbers MUST be frozen before narrative writing).
- Admin: bump changelogs v0.9 → tag `v0.9` on both repos; push origin to GitHub; mint Zenodo DOI at v1.0 submission.

---

## [v0.2.1] — 2026-09-03 — College ANOVA df correction + v0.9 heterogeneity analysis run
### Corrected (1 item carried over from v0.2)
- **anova_df_within 3,675 → 3,674** (both in FINAL_ANALYSIS_PROTOCOL §7 and final_config.yaml canonical_numbers).
  Actual: 3,713 non-NaN RTAS rows − 39 colleges. The previous 3,675 was an approximation
  (3,714 − 39) made before explicitly dropping the single all-NaN RTAS row from the
  college-ANOVA substrate. Confirmed `F(38, 3674)` by direct run.

### Added (v0.9 stage ① heterogeneity — regenerated with primary rtas_mini_mean)
- `03_FINAL_ANALYSIS/heterogeneity/_build.py` : single entry point (seed 42, frozen RTAS).
  Outputs 9 files, all with canonical-number audit baked in:
  - Project level: `anova_project_level.csv` F(2,3710)=33.0 p=6e-15 η²=1.75%;
    `project_level_summary.csv` national 0.147 > provincial 0.138 > university 0.120;
    `tukey_project_level_pairwise.csv` all 3 pairs significant;
    `project_level_top_vs_bottom_cohensd.csv` Cohen d=0.349 national vs university.
  - College level: `anova_college.csv` F(38,3674)=204 p≈0 η²=67.9% (df matches canonical);
    `college_rtas_summary_all.csv` (all 39); `college_rtas_top20.csv` (name font 10pt later).
  - `heterogeneity_audit_log.json` — canonical checks all true (40/39 colleges, 1940 supervisors).

---

## [v0.2] — 2026-09-03 — RTAS FROZEN

### Milestone status
✅ **FROZEN.** Any change to §1 (data sample), §2 (RTAS), or §7 (canonical numbers)
of `FINAL_ANALYSIS_PROTOCOL.md` below v0.9 MUST first open a new changelog entry and
bump the protocol to at least v0.3. Do not silently edit these sections.

### Added
- New private working repo `D:\vc-task\RTAS_FINAL_PROJECT` with 21 subdirectories and 2-repo architecture (private + GitHub public).
- `00_README/FINAL_ANALYSIS_PROTOCOL.md` — single source of truth, 8 sections: data sample freeze, RTAS freeze, downstream pipeline, provenance rules, reproducibility, ethics, canonical number replacements, versioning milestones.
- `00_README/final_config.yaml` — machine-readable parameter sheet for all 06_CODE scripts (v0.2 schema).
- `00_README/README.md` — repo layout diagram, golden rules, milestones, quickstart.
- `00_README/CHECKSUMS.md` — MD5 hashes of 12 frozen artefacts computed by `_helpers/_gen_checksums.py`.
- Folder `02_RTAS_MODEL_SELECTION/` populated: 5 MiniLM RTAS variants (mean, top5, top10, top20, centroid) on 3,714 projects; `rtas_model_selection.csv` with 5-criteria evaluation; `PRIMARY_RTAS.json`; `selection_report.md`; 6 replicate scripts (01 map → 06 verify); embeddings/ and human_validation/ subfolders.
- `01_DATA/final_analysis/table5_project_dataset_n3714.csv` promoted as canonical project dataset.
- `01_DATA/interim/author_to_college_lookup.csv` + `02_RTAS_MODEL_SELECTION/paper_college_year_map.csv` (12K papers → college × year; 64.5% matched, 1.83 colleges/paper after homonym skipping).

### Changed (with respect to earlier paper draft / historical files)
- **Primary RTAS algorithm changed** from the inconsistent dual ("mean in formula, Top-5 in flowchart") to a single frozen definition: `rtas_mini_mean` = MiniLM mean cosine(project_title, college-year paper titles), window cumulative [2020, project_year].
- **Year window corrected:** "5-year contemporaneous" claim → cumulative [2020, t] (no pre-2020 OpenAlex data exists on disk). Honest limitation added to protocol.
- **OpenAlex substrate pinned:** 12,000 first-batch subset (title-only); 35,721 claimed but not on disk → honest labelling in protocol.
- **College count 40 vs 39 explained:** 40 total, 39 in HLM substrate because 1 college has no matched-author papers (all-NaN RTAS → dropped silently by mixed models).
- **Supervisor count 1,899 → 1,940** unique; 1,899 labelled as outdated early-dataset value.
- **Top5% supervisors 94 → 97**, Gini 0.744 → 0.767, Top5% national share 30.4% → 34.0%, ANOVA df_within 3,674 → 3,675.
- **RTAS validity numbers clarified:** 0.098 = old topic-based RTAS (legacy); 0.405 = new paper-based Primary RTAS C1; 0.56 = human inter-rater reliability (separate metric).

### Downgraded
- MiniLM top5 / top10 / top20 / centroid → sensitivity analysis only.
- Original topic-based `rtas_sbert` → convergent validity proxy (C5); no longer the primary score.

### Deferred
- BGE-M3 embeddings & variants (torch c10.dll WinError 1114 on this machine). Status tag: "deferred robustness". C5 currently uses convergent validity vs legacy topic-based RTAS; protocol says C5 becomes MiniLM↔BGE inter-model Spearman once BGE encodes.

### Known honest limitations (written into protocol §2 / §7)
1. 12K first-batch subset, not full 35,721 OpenAlex.
2. Title↔title only (no abstract available in 12K file); title-vs-fulltext robustness N/A (C3 repurposed to K-stability).
3. Window cumulative, not 5-year rolling.
4. Paper→college mapping = advisor Chinese-name pinyin match; homonym collisions skipped. 64.5% coverage.
5. College ICC = NaN (mixedlm singular fit); stability proxied by year SD.

---

## [v0.1] — 2026-09-02 — Model-Selection Experiments Baseline
(Historical milestone marking when MiniLM 5-variants pipeline ran for the first time on 3,714 projects. Outputs superseded and refined by v0.2.)
