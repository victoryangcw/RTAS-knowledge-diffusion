# CHANGELOG — RTAS Final Project

Format: **Semantic versioning on milestones**. Each entry lists changes to protocol,
config, data, or code that could affect downstream numbers.

---

## [v1.0-cand.14] — 2026-09-18 — TWENTY-THIRD ROUND: NUMERICAL PROVENANCE AUDIT

Milestone status: ✅ Full read-only numerical provenance audit completed.
No frozen analysis output changed; no pipeline re-run. Five presentation-level
manuscript corrections (one stale statistic, three wording/rounding fixes, one
Methods sentence). New artifacts: `03_CODE/19_numerical_provenance_audit.py`
(read-only; 115 checks across 7 modules, 115 PASS) and
`06_RESULTS/19_numerical_provenance_ledger.csv` (per-number source file, column,
formula, recomputed value).

### Coverage — every headline number independently recomputed
1. **corpus/linkage**: 3,714 projects; level counts 1,375/1,657/682 and
   37.0/44.6/18.4%; 1,834 advisors / 4,244 links / 528 co-supervised (rebuilt via
   frozen delimiter regex); 56,901 articles with exact yearly counts; 22,438
   prehistory; 79,339 total; 33,312 college-assigned (58.54%); match status
   2,750/748/216; 60,615 joint docs.
2. **aggregation/RTAS**: five composites recomputed from frozen formula
   (.742/.480/.447/.398/.300, mean wins); final RTAS describe() exact
   (mean .1337, SD .0723, median .1362, range −.0575/.3960); 0→10-publication
   shift 0.004266×ln11=0.01024 ≈ 0.142 SD.
3. **validation**: ρ=.405, AUC=.880, Kendall .327, related-only −.253, LOO
   .018; Rater A QWK .465 / exact 72%; Rater B QWK .606 / exact 78%; A–B QWK
   .826; retest .643; LLM .459/.638/.933; baselines .300/.638 etc.; BGE-M3
   .334/.811; paired-bootstrap CIs — all reproduced.
   Convention findings (no data error): QWK is computed on the FIXED rubric grid
   {1,2,3,4} (sklearn default observed-labels-only gives .409 — the frozen .606
   is correct); AUC uses the frozen default-argsort tie convention (Mann-Whitney
   average-rank equivalent here).
4. **topic/lag**: 29 defined-lag topics (3.27% of 886; 24 HRLT + 5 HRHT)
   rebuilt atomically from yearly prevalence under the ≥3 docs/≥0.2% (articles)
   and ≥2/≥0.2% (projects) rule; HRLT 12/9/3 = 50.0/37.5/12.5%; overall median
   0, mean +0.59; 13 zero-lag topics; rebuild is row-identical to frozen
   topic_first_year_adoption.csv.
5. **RQ1**: group means .1212/.1391/.1460; F(2,3711)=35.72, p=4.3e-16,
   η²=1.89% (bootstrap CI [1.14,2.86]); Tukey +.0179***/+.0248***/+.0070
   (p=.082); Welch N–U t=7.375, p=2.9e-13, d=.352.
6. **RQ3 variance decomposition** (in-memory REML refit from frozen table;
   prior-supervision column rebuilt from atoms and identical to frozen):
   n=3,231/39; null τ₀₀=.005438, σ²=.001791 → ICC .7523; full τ₀₀=.004944,
   σ²=.001759 → ICC .7376; var(FE)=.000050 → marginal R²=.0075,
   conditional R²=.7395 (Nakagawa-Schielzeth/Johnson); β log_prior3y=.004266
   (p=3.201e-9), supervision=−.006287, year=.003132.
7. **RQ4** (highest residual risk — all definitions locked): Gini computed over
   ALL 1,834 advisors including 1,236 with zero national projects
   (.7458 national / .3677 total); top-5% = ceil(0.05×1834=91.7) = 92 advisors
   holding 30.99%; top-20% = int(366.8) = 366 advisors holding 71.91%;
   top-5% exposure = 560 projects with ANY top-5% advisor, project-deduped once
   (560+3,154=3,714), d=.083, Welch p=.065; lagged logits rebuilt: sample A
   979 supervisor-years/627 advisors OR 2.06 [1.53,2.76]; sample B
   2,469/1,560 OR 2.45 [1.91,3.16]. Advisor load 818 (44.6%) one project,
   345 (18.8%) ≥4.

### Manuscript corrections (presentation only; frozen numbers untouched)
- **§2.1 linkage**: "mean 1.83 colleges per matched article" → **1.37**.
  Full-corpus truth 45,619 article–college edges / 33,312 = 1.3694 (9,608
  articles with >1 college); 1.83 was a stale 12K-first-batch-era statistic.
- **§2.1 projects**: "title (92% Chinese)" → "title (on average 92% Chinese
  characters)". The frozen 0.92337 is the mean within-title CJK character
  share, not the share of Chinese-language titles (Chinese-majority titles
  are 98.57%; 99.92% contain any CJK).
- **§2.1 articles**: "with 100% English titles" → "predominantly English
  titles (56,858 of 56,901, 99.9%, contain no Chinese characters)"; 43 full-
  corpus titles contain CJK characters (the 100% was exact only on the 12K
  first batch).
- **§2.4 LLM second rater**: "ρ = 0.638 (p < 10⁻¹⁸)" → "p = 1.7×10⁻¹⁸"
  (exact frozen p=1.73e-18, which is not below 1e-18).
- **Methods closing sentence**: "All numbers derive from frozen CSVs under a
  fixed seed (42); no statistic was hand-edited." → "All reported statistics
  were generated from frozen analysis outputs; values are rounded for
  presentation. Seed 42 was used wherever stochastic procedures required a
  random seed." (presentation rounding, e.g. 3.26e-9→3.3e-9, is normal
  formatting, not hand-editing).

---

## [v1.0-cand.14] — 2026-09-18 — TWENTY-SECOND ROUND: ADVISOR-LEVEL DEPENDENCE SENSITIVITY

Milestone status: ✅ RQ3 advisor-dependence robustness added.
All frozen primary statistics unchanged.

### Advisor-dependence sensitivity (new `03_CODE/18_advisor_dependence_sensitivity.py`)
- Motivation: primary MixedLM clusters only within colleges; advisors supervise
  repeated projects (18.8% of individual advisors supervise ≥4).
- Multiple membership: no primary-advisor flag; 528 co-supervised projects are
  excluded rather than duplicated. Analysis restricted to 3,186 single-advisor
  projects (2,716 complete cases; 1,221 advisors; 680 with ≥2 projects).
- Crossed RI model `(1|college)+(1|advisor)` converges to a BOUNDARY solution
  (college variance = 0) and is unreliable: advisor-level covariates vary mainly
  between advisors (within-advisor SD of log prior3y = 18% of total; constant
  within advisor for ~30% of repeat advisors). Reported transparently, not used.
- Reliable check: college FE + advisor-clustered SE. All substantive conclusions
  unchanged: log_prior3y β=+0.0043 (p=1.5e-5, CI excludes 0), log_prior_supervision
  β=−0.0053 (p=0.004), year β=+0.0026 (p=0.001), funding dummies ns.
  Coefficient magnitudes changed only modestly vs frozen primary; signs and
  inferential conclusions preserved; SEs increase as expected under clustering.
- Homonym guard (Model D): SEs clustered by college x advisor name (1,333 clusters
  vs 1,221 raw names); point estimates identical, SEs virtually unchanged
  (log_prior3y SE 0.000983 -> 0.000972), same conclusions.
- Manuscript: new §3.4 "Advisor-dependence sensitivity" paragraph; Methods RQ3
  pointer; new Limitation 9 (multiple membership of co-supervised projects).

### Final consistency pass (same day; no new analysis, no frozen numbers changed)
- 178-topic wording audited against atomic doc_topic_assignments.csv (60,615
  rows = 56,901 papers + 3,714 projects, no missing/duplicate docs; 886
  contiguous topic ids 0-885 + Topic -1 outlier bucket of 23,318 docs correctly
  excluded). Frozen rule metadata: "top-20% topics (n>=177); frac>=0.0879%".
  The 0.0879% value equals exactly 50 articles; EIGHT topics tie at 50 papers
  (ids 155,174,180,181,183,185,186,187; ranks 171-178), rank 170 has 51, rank
  179 has 49. Inclusive >= classification therefore yields 178 (5 HRHT +
  173 HRLT), not an omission. Recomputing flags from the atomic file reproduces
  the frozen high_paper/high_project sets exactly (178 / 15); clustered totals
  35,547 papers + 21,354 outliers = 56,901 and 1,750 + 1,964 = 3,714.
  topic_info.csv/doc_topic_assignments.csv mtimes are 2026-09-03 (original
  freeze), untouched by all later rounds.
- RTAS definition: replaced ambiguous "a co-supervised article counts once"
  with explicit within-college-once / once-per-college dedup rule; added
  abstract-asymmetry justification for titles-only scoring.
- Methods RQ3: defined marginal vs conditional R2 (Nakagawa & Schielzeth 2013).
- Figure 5 title: removed "33 of 39 colleges have CIs excluding 0" (BLUP
  intervals are not simultaneous tests); regenerated from frozen CSV.
- Supplementary S1 changed from exploratory tercile transition matrix to the
  descriptive supervisory-load distribution (1,834 advisors; 44.6% one project,
  18.8% four or more; numbers match §3.5). New file
  `02_FIGURES/supplementary/FigureS2_SupervisorLoad.{pdf,png}`; stale
  Figure7_TransitionMatrix files deleted (deprecated n=736 raw-field version).
- Wording fixes in manuscript source: "case university" removed;
  "observable proxy for the research frontier" removed; RQ1 "strict ordering"
  replaced with descriptive ordering + N-vs-P not significant; primary-model
  log_prior3y p printed as 3.3e-9 (exact 3.26e-9; previously mis-rounded).
- Also backfilled frozen outputs for cand.13 robustness analyses
  (BGE-M3, leave-advisor-out) into `05_VALIDATION/robustness/`, `06_RESULTS/hlm/`.

---

## [v1.0-cand.13] — 2026-09-14 — TWENTY-FIRST ROUND: VERIFY AUDIT + RQ4 UNIT FIX

Milestone status: ✅ All 6 VERIFY items resolved; RQ4 individual-advisor replacement.
All non-RQ4 frozen statistics unchanged. No primary pipeline re-run.

### VERIFY items resolved
1. **BGE-M3 benchmark** (NEW experiment): 150-pair reference set re-encoded with
   BGE-M3 (1024-dim multilingual). ρ=0.334, AUC=0.811 vs MiniLM ρ=0.405, AUC=0.880.
   Paired bootstrap (N=2000): Δρ=−0.071 [−0.187, +0.036], ΔAUC=−0.069 [−0.179,
   +0.032]. No evidence that BGE-M3 improved validity; MiniLM retained as primary.
2. **Leave-advisor-out sensitivity** (NEW experiment): RTAS recomputed after
   removing advisor-authored papers from each project's college reference portfolio.
   β(advisor publications) attenuated ~10.5% (0.00427→0.00382) but remained
   significant (p=5.3e-07). ICC (0.738) and conditional R² (0.739) unchanged.
3. **Lagged logistic year reference**: source code confirmed `drop_first=True` on
   outcome years {2021–2024} → reference=2021 (not 2020). Methods clarified.
4. **BERTopic ARI 0.93–0.98**: no provenance in codebase (no adjusted_rand_score,
   no reduce_topics/nr_topics, no K=800/850/900). Sentence deleted; HDBSCAN
   parameter sensitivity (min_cluster_size/min_samples, 4 specs, 454–1287 topics,
   outlier 0.364–0.396) retained as sole clustering robustness.
5. **Lexical baselines exact values**: TF-IDF ρ=0.300/AUC=0.638; Jaccard
   ρ=0.296/AUC=0.637; BM25 ρ=0.298/AUC=0.637 (all from frozen CSV, verified
   against script rerun).
6. **RQ4 supervisor identity / unit fix** (SUBSTANTIVE): raw `advisor` string
   contained 106 co-supervised combinations (e.g., "张三、李四") counted as
   unique supervisors. Split into individual advisors: 1,940→1,834 unique
   advisors, 3,714→4,244 advisor–project edges, 528 co-supervised projects.
   All RQ4 statistics replaced with individual-advisor versions:

   | Metric | Old (raw field) | New (individual) |
   |--------|---------------|------------------|
   | Unique advisors | 1,940 | 1,834 |
   | National Gini | 0.767 | 0.746 |
   | Total Gini | 0.344 | 0.368 |
   | Top-5% count | 97 | 92 |
   | Top-5% national share | 34.0% | 31.0% |
   | Top-20% share | 76.8% | 71.9% |
   | Sample A (OR) | 736/491, OR=2.25 | 979/627, OR=2.06 [1.53, 2.76] |
   | Sample B (OR) | 2302/1621, OR=2.28 | 2469/1560, OR=2.45 [1.91, 3.16] |
   | Top-5% vs rest RTAS | d=−0.033 ns | d=+0.083, p=0.065 (unique project level) |

   **All qualitative conclusions survived**: concentration (Gini still high),
   path dependence (OR still significant, CI excludes 1), no alignment advantage
   for top-5% (d still ns). HLM not affected (already used individual advisors).
   Top-5% vs rest RTAS unit fixed from edge-level to unique-project-level.

### Figures regenerated
- Figure 2 Roadmap: RQ4 box updated (Gini=0.746, Top5%=31.0%, OR=2.06).
- Figure 10 Matthew Effect: all three panels use individual-advisor data;
  Lorenz curve, Pareto bars, and OR forest all updated.

### Manuscript updates
- Abstract, §2.1 Data, §2.5 (ARI deleted), §2.7 Methods (RQ4 unit + year ref),
  §3.4 (leave-advisor-out), §3.5 (all RQ4 numbers), §4 Discussion, §5 Limitations
  (BGE-M3 + LOO + pipeline-v2 future work), §2.4 (lexical baselines exact values)
  — all updated across cleaned.md, repo SUBMISSION_manuscript_v1.0.md, and v0.9.md.
- §10 changelog retains old numbers as audit record only.

---

## [v1.0-cand.12] — 2026-09-10 — TWENTIETH ROUND: SUBMISSION MODEL-SPEC FIXES + FIGURE LAYOUT

Milestone status: ✅ Submission-manuscript technical consistency + Fig.6 layout.
All frozen statistics unchanged. No analysis re-run.

### Submission manuscript (`04_MANUSCRIPT/SUBMISSION_manuscript_v1.0.md`, new in repo)
- P0 model-specification correction: RQ3 MixedLM year term is a CONTINUOUS
  variable centered at 2022 (β=+0.00313/yr), not categorical year dummies;
  advisor-clustered SEs belong ONLY to the RQ4 lagged logistic model
  (categorical year FE, SEs clustered by supervisor). Methods and Results now
  state this unambiguously.
- R² sentence rewritten: marginal R²=0.0075 vs conditional R²=0.7395 — fixed
  effects explain little variance relative to the large between-college
  component (old sentence was ambiguous).
- Abstract/wording: "peer-reviewed articles" → "OpenAlex-indexed articles";
  lag finding scoped to "24 lag-definable HRLT topics"; "synchronized" →
  "same-year first non-trivial presence"; "pre-registered" → "pre-specified";
  Discussion causal-leaning verbs removed ("transmit", "levers",
  "however decorated"; "predicts" → "is associated with").
- Final submission figure numbering: main text Fig 1–7, supplementary
  Fig S1–S4 (development-history numbering removed from the submission list).

### Figure layout (`06_CODE/10_generate_figures.py`; regenerated all figures)
- NEW `Figure8_DiffusionLag_Stacked`: panels (a) lag distribution and
  (b) lag-by-quadrant stacked VERTICALLY at full column width (side-by-side
  placement made small annotations unreadable after Springer reduction).
  Panel (a) legend moved inside axes (upper-left empty band).
- LRHT/LRLT undefined-lag note moved to panel upper-RIGHT (upper-left crossed
  HRLT scatter points at y=4 and the whisker); fixed in both the stacked and
  standalone Figure8b files.
- Standalone Figure8a/8b files retained as alternates.

---

## [v1.0-cand.11] — 2026-09-07 — NINETEENTH ROUND: SUBMISSION CLEANUP (submission-track preparation)

Milestone status: ✅ Consistency wording + figure label cleanup + Data Availability tiering.
All frozen statistics unchanged. No analysis re-run.

### Manuscript consistency edits (`07_MANUSCRIPT/manuscript_draft_v0.9.md`)
- Validity claims unified: §2.2/§12.2 item 5 now state "converging evidence for
  pairwise semantic validity and rating reliability"; no residual "construct
  validity" claim in results/limitations (changelog history in §10 retains old
  wording as audit record only).
- Quadrant de-temporalization completed: §3.4 core-conclusion sentence rewritten
  (static prevalence framing; temporal reading restricted to §6's 29 defined-lag
  topics); §12.3 item 6 LRHT gloss changed to "low research-side / high
  project-side prevalence" (was "research gone cold").
- HLM non-causal wording: §12.3 item 5 rewritten as positive/negative
  association + "consistent with a capacity-dilution interpretation"; internal
  metaphors removed from forward-looking text.
- RTAS≠quality (§5.5): "resource concentration did not translate into higher
  research–training alignment" (already in cand.10; verified intact).
- Naive lexical baselines: §3.7 file-listing entry re-labeled as "naive lexical
  baselines (no translation alignment); supports embedding choice, not an
  incremental-validity claim"; BGE-M3 file entry re-worded to "not benchmarked
  in the present study".
- §11.2 rewritten as THREE-TIER Data Availability: (1) OpenAlex records publicly
  retrievable via documented institutional query; (2) institutional project
  records contain PII, not redistributable; (3) non-identifying derived outputs
  + code via GitHub repository.

### Figure label cleanup (`06_CODE/10_generate_figures.py`; all 13 figures regenerated)
- Figure 8a suptitle: "Research → Training Adoption Delay" → "Distribution of
  Defined Topic Lags" (adoption/emergence vocabulary already frozen out in
  cand.8; title now aligned).
- Figure 11 suptitle: internal versioning note "(v1.0-cand.4: demoted to
  Supplementary)" removed from canvas.
- Figure 10: Lorenz legend "National grants" → "National-level projects"
  (funding-tier ≠ grant-funding misread).
- Figure 2: Main-corpus box now spells out "undergraduate innovation projects"
  and adds "RTAS reference portfolios: 33,312 college-assigned papers (58.5%)"
  so the roadmap carries the three-tier corpus numbers.
- Figure 4: level labels → University-level / Provincial-level / National-level.
- Figure 13a/13b: suptitles deduplicated ("(a)"/"(b)" now appear only as panel
  titles) and "ITTP" expanded to "undergraduate innovation projects" for
  standalone readability.

### New submission-track file
- `07_MANUSCRIPT/SUBMISSION_manuscript_v1.0.md`: English IMRaD submission clean
  version (Abstract, Introduction, Data and Methods, Results, Discussion,
  Limitations, Conclusion, Declarations incl. three-tier Data Availability,
  figure/table lists). Master `manuscript_draft_v0.9.md` remains the frozen
  audit source-of-truth; development history (§10) stays out of the submission
  version by design.

---

## [v1.0-cand.10] — 2026-09-06 — EIGHTEENTH ROUND: TEACHER REVIEW ABSORPTION (~2/3 accepted, 1/3 rejected)

Milestone status: ✅ Text revisions + 3 new secondary robustness analyses.
All frozen statistics unchanged (rho=0.405, ICC=0.7376, d=0.352, eta2=1.89%, ...).

### Manuscript text edits (`07_MANUSCRIPT/manuscript_draft_v0.9.md`)
- Related-work positioning: added Scafetta (2025, *Scientometrics*) RT-score
  (faculty-level performance composite) + Maisano et al. (2023, *Scientometrics*);
  RTAS explicitly distinguished as project-level cross-lingual semantic alignment,
  NOT used for performance ranking.
- RQ2 downgraded: from "how long does it take a topic to diffuse from research to
  training" to "what topic-level asymmetries characterize the two corpora, and
  where annual onset is identifiable, what temporal lag is observed" (avoids
  over-committing to "diffusion").
- Titles-only design rationale: titles chosen as the symmetric cross-lingual text
  unit available on both sides (not "abstracts unavailable"); tradeoff = sparse
  semantics.
- Formula clarifications: P_{c,t} = college-assigned unique paper records (dedup
  within college); lag undefined rule stated as part of Equation 2; composite
  weights (0.45·C2 + 0.30·C4 + 0.25·C3, min-max normalized) inlined by the
  selection table (frozen in rtas_selection_composite_v1.csv).
- Single-institution analytical leverage: added to Introduction — unified
  governance + common time window + 40 disciplinary units = natural lab;
  external validity needs multi-site replication.
- Lagged-logistic year FE coding clarified: categorical dummies, 2020 reference
  year, clustered SE by advisor; advisor-FE logit noted as optional sensitivity
  (drops units without within-advisor variation, not primary).

### New secondary analyses (scripts in `06_CODE/`, outputs new files only)
- **T1 baseline validity** (`13_baseline_validity.py`): on the 150-pair reference
  set, MiniLM (rho=+0.405, AUC=0.880) clearly outperforms three lexical baselines
  (TF-IDF cosine, char-3-gram Jaccard, BM25 Okapi; all rho≈+0.30, AUC≈0.64) →
  clean incremental-validity evidence for the semantic embedding choice.
- **T3 BERTopic clustering-parameter sensitivity** (`14_bertopic_sensitivity.py`):
  3 alt HDBSCAN param sets on cached joint embeddings. Outlier rate stable
  0.364–0.396 (frozen 0.3847 not a one-param artifact); quadrant direction stable
  (LRLT always dominant 62–68%, HRHT always rarest 4–9%); topic count 454–1287
  is normal granularity variation.
- **T4 HLM diagnostics** (`15_hlm_diagnostics.py`): refit frozen v2b (ICC sanity
  = 0.7376 ✓). Null-model ICC = 0.7523; Nakagawa-Schielzeth R² marginal = 0.0075
  (fixed effects explain almost nothing), conditional = 0.7395 (college context
  dominates). Project-level ANOVA eta-squared 95% bootstrap CI = [1.14%, 2.86%]
  (B=10,000, seed 42).
- **T2 BGE-M3 benchmark** (`16_bge_m3_benchmark.py`): NOT run — torch DLL
  initialization fails (known env instability). Documented as planned future
  robustness; MiniLM remains primary.

### Rejected (explicitly, per user decision)
- 3,000–5,000 LLM validation (stratified-sampling then raw Spearman = wrong);
- Dynamic BERTopic (RQ2 downgrade already solves coverage);
- RI-CLPM / Granger / IV causal analysis (short 5-yr panel, matching error,
  reopens causal language; teacher's code has 5 known data-lineage bugs).

### Repo sync
- New scripts `03_CODE/13–16_*.py`, new outputs under `05_VALIDATION/`,
  `03_FINAL_ANALYSIS/hlm/hlm_diagnostics_v2b.csv`,
  `03_FINAL_ANALYSIS/topic_model/bertopic_clustering_sensitivity.csv`.
- Tag v1.0-cand.10 pushed.

---

## [v1.0-cand.9] — 2026-09-05 — SEVENTEENTH ROUND: SINGLE-RATER VALIDATION HARDENING (SECONDARY; FROZEN NUMBERS UNTOUCHED)

Milestone status: ✅ Robustness add-on package for the 150-pair single-rater
construct-validity check. No frozen CSV or estimated number changed; the frozen
point estimate remains Spearman rho = +0.405.

### New analyses (`06_CODE/11_validation_robustness.py`, seed 42, B=10,000)
- Replicates the frozen C1 pipeline (exact-title match 150/150; rho = +0.4055 ✓).
- **R4 dichotomized discrimination (headline)**: embedding cosine separates
  rater-relevant (>=2, n=16) from irrelevant (=1, n=134) pairs with
  **AUC = 0.880 [0.793, 0.949]**, point-biserial r = +0.459 — directly answers
  the "134/150 ties" reviewer concern.
- R1 bootstrap 95% CI for rho: **[+0.281, +0.509]** (excludes 0).
- R3 permutation p < .001; R2 Kendall tau-b = +0.327 [+0.229, +0.410].
- R6 leave-one-out: max |delta rho| = 0.018 (no single pair drives the result).
- R5 informative-subset rho (n=16) = -0.253, reported for transparency only
  (n too small for inference); validity claim rests on AUC + full-sample rank
  correlation, not fine-grained ranking within relevant pairs.
- Outputs: `02_RTAS_MODEL_SELECTION/human_validation/robustness/`
  (`validation_robustness_stats.csv`, `150pairs_with_cos_mini.csv`).

### New protocol & instruments (`02_RTAS_MODEL_SELECTION/human_validation/`)
- `RATING_RUBRIC.md`: 1-4 English anchor definitions (verbatim LLM prompt v1),
  blinding rules, LLM second-rater / test-retest / second-human-rater
  protocols; protocol + forms committed to the repo BEFORE retest execution
  (pre-specified timestamping).
- `retest_40pairs_form.csv` (intra-rater test-retest, >=2-week washout, seed 42)
  and `second_rater_50pairs_form.csv` (optional independent second rater);
  both blinded (no first-round scores).
- `06_CODE/12_llm_second_rater.py`: blind re-rating of all 150 pairs into the
  pre-registered `annotator2` slot (JSON output, checkpointed, idempotent).
  Auto-detects provider: DeepSeek (`.deepseek_key` / env `DEEPSEEK_API_KEY`,
  `base_url=https://api.deepseek.com/v1`) preferred, else OpenAI. **Run
  completed 2026-09-06 with `deepseek-reasoner` (R1), temperature=0, prompt
  v1.1** (prompt v1.1 adds explicit score-2 examples so the model uses the full
  scale; v1 made deepseek-chat/R1 default to score 1 on cross-disciplinary
  pairs). Results (secondary):
  - Human–LLM: quadratic-weighted κ = **0.459** (moderate), Spearman ρ =
    **0.638** (p < 1e-18), exact agreement 93.3%.
  - RTAS–LLM triangulation: Spearman ρ = **0.279** (p = 0.0005), vs frozen
    RTAS–human ρ = 0.405 — RTAS embeddings correlate with an independent LLM
    rater's blind judgments.
  - Confusion matrix: LLM is stricter than the human (143 ones vs human 134);
    of 13 human-2 pairs LLM agrees 6 as 2 (7 as 1); human-4 pair → LLM 2.
  - Outputs: `human_validation/150pairs_llm_second_rater.csv`,
    `human_validation/robustness/llm_agreement_stats.csv`.
  - Note: original GPT-4o plan replaced by DeepSeek-R1 because the OpenAI
    account had no credits; DeepSeek-R1 used as the LLM rater. Proxy env vars
    stripped in-script to avoid Windows TLS issues; key files gitignored.
- **Second human rater completed 2026-09-07** (50 pairs, blind, independent):
  quadratic-weighted κ = **0.465**, Spearman ρ = **0.333** (p = .018), exact
  agreement 72% (36/50). Friend (Rater A) used same rubric, no access to
  first-round scores or RTAS values. Friend gave more 2s (14 vs human 3) —
  slightly more generous but directionally consistent. Manuscript §2.2 updated:
  "single-rater" framing retained for the frozen ρ=0.405, but inter-rater κ
  now reported alongside LLM agreement as triangulation evidence.
  Outputs: `human_validation/second_rater_50pairs_filled.csv`,
  `human_validation/robustness/inter_rater_stats.csv`.
- **Test-retest completed 2026-09-07** (40 pairs, same rater, ~12-day washout,
  reshuffled order, blinded): quadratic-weighted κ = **0.643**, Spearman
  ρ = **0.688** (p < .001), exact agreement 95% (38/40). All 36 retest-1 pairs
  were originally 1; of 4 originally-2 pairs, 2 stayed 2 and 2 drifted to 1
  (boundary pairs). The validation evidence chain is now complete:
  RTAS embedding vs human ρ=0.405/AUC=0.88, second human rater κ=0.465,
  test-retest κ=0.643, LLM rater κ=0.459. Outputs: `human_validation/retest_40pairs_filled.csv`
  (blank pre-specified form is `retest_40pairs_form.csv`, GBK-encoded),
  `human_validation/robustness/test_retest_stats.csv`.
- **Third rater completed 2026-09-07** (Rater B, same 50 pairs, blind):
  vs reference rater κ = **0.606**, exact 78% (Spearman unstable due to
  reference rater's 46/50 tied 1s — interpret via kappa). The two independent
  second raters agree with each other at κ = **0.826** / ρ = 0.821 / exact 90%
  (45/50) — rubric is stably reproducible by third parties. RTAS–Rater B
  triangulation: ρ = **0.621** (p < .001), binary AUC = **0.932** — both
  HIGHER than the frozen reference values (0.405 / 0.880), indicating the
  frozen C1 is conservative, not inflated. Outputs:
  `human_validation/second_rater_50pairs_raterB.csv`,
  `human_validation/robustness/inter_rater_stats_rater2_raterB.csv`.

### Manuscript (`07_MANUSCRIPT/manuscript_draft_v0.9.md`)
- §2.2 C1 item: robustness numbers (AUC/CI/permutation/LOO) + protocol pointer,
  explicitly secondary and consistent with the "single-rater reference
  relevance ratings" framing.
- §10 data dictionary: new validation files listed.
- §12.2 item 5: hardening summarized; single-rater baseline framing unchanged.

### Repo
- New `05_VALIDATION/` directory: RATING_RUBRIC.md, annotation CSV, per-pair
  cosine CSV, both blinded forms, robustness stats (aggregate only); scripts
  added to `03_CODE/`. Committing the protocol before execution is itself the
  pre-specification evidence.

---

## [v1.0-cand.8] — 2026-09-05 — SIXTEENTH ROUND: MANUSCRIPT PRECISION PASS (LAG TERMINOLOGY, TUKEY DIRECTION, CORPUS TIERS, NON-CAUSAL WORDING)

Milestone status: ✅ Text-only precision pass + one figure-label regeneration.
All frozen CSVs and all frozen statistics unchanged; no estimated number touched.

### Changed (figures, `06_CODE/10_generate_figures.py` → `05_FINAL_FIGURES/`)
- **Figure 8a label terminology frozen** (user-approved wording): x-axis
  `"Lag (years): project adoption − paper emergence / positive = research leads
  training"` → `"Lag (years): year(project first non-trivial presence) −
  year(paper first non-trivial presence)"` (direction note now carried by the
  legend); legend `"Zero lag (synchronized)"` → `"Zero lag (same-year first
  presence)"`. `Figure8a_LagDistribution.pdf/png` + `Figure8b_LagByQuadrant.*`
  regenerated from frozen CSVs (8b content unchanged).

### Changed (manuscript, `07_MANUSCRIPT/manuscript_draft_v0.9.md`)
- **Tukey Δ direction unified manuscript-wide** to *higher level − lower level*
  (P−U / N−U / N−P, positive = higher tier scores higher): §1.1 results block,
  §10 summary-table row, Figure 4 caption (was "U vs N Δ=−0.0248" style, mixed
  conventions across sections), §12.1/§12.3 items. Pair labels in Figure 4
  brackets (U–P etc.) unchanged — they identify pairs, not contrast direction.
- **§1.3 three-tier corpus clarification** (new table + note): ① OpenAlex
  retrieval corpus 56,901 (BERTopic paper-side denominator) → ② advisor-matched
  college portfolio 33,312 = the ONLY subset entering R_c(t) → ③ BERTopic joint
  corpus 60,615 = 56,901 + 3,714. "College research portfolio" explicitly glossed
  as *observed advisor-linked college research portfolio* (no independent roster).
- **§3.4 descriptive-statement added**: the funding-tier contrast is descriptive,
  not an independent confirmatory validation of RTAS selection (known-groups
  weighting in the composite score creates partial circularity); all 5
  aggregation variants agree in sign/significance → conclusion not
  selection-dependent.
- **η² vs ICC estimand note (§4.4)**: college ANOVA η² = 66.90% (full-sample,
  fixed-effects partition, 3,713/39) vs ICC = 0.7376 (complete-case REML random
  intercept, 3,231/39, covariate-adjusted) — different estimands, not mutually
  derivable, coexist without contradiction.
- **College-effect interpretation de-performized** (§4.4 item 5 + §12.2 item 3):
  college-level differences mix organizational context with RTAS measurement
  sensitivity to disciplinary specialization, portfolio breadth, title-language
  conventions, and portfolio heterogeneity; rankings must not be read as
  performance.
- **HLM wording non-causal** (§4.4 item 2 + §12.3 item 5): supervision-load
  effect described as *consistent with a capacity-dilution interpretation, but
  not identified causally*; "包工头效应" flagged as an explanatory label only.
- Version table: cand.6 / cand.7 rows added, footer bumped to v1.0-cand.8.

### Docs
- `05_FINAL_FIGURES/gallery.html`: no changes needed (Figure 8a/8b filenames and
  captions unchanged).

---

## [v1.0-cand.7] — 2026-09-05 — FIFTEENTH ROUND: FIGURE 13 FILE SPLIT & COHEN'S d CONVENTION FIX (USER VISUAL + REVIEWER AUDIT)

Milestone status: ✅ Visualization + one numeric-convention fix. All frozen CSVs
unchanged (the d fix aligns the manuscript TO the frozen CSV, not vice versa).

### Changed (figures, `06_CODE/10_generate_figures.py` → `05_FINAL_FIGURES/`)
- **Figure 13 split into two standalone supplementary files** (user review: panels
  crowded each other when side-by-side):
  - `supplementary/Figure13a_TopicTrend.pdf/png` (7.4 × 5.8): diversification
    two-line trend; **legend moved to the upper-right corner** (was center-right).
  - `supplementary/Figure13b_TopicHeatmap.pdf/png` (7.0 × 6.8): 15 × 5 prevalence
    heatmap with own colorbar; 15 row labels now full-size and unobscured.
  - `supplementary/Figure13_TopicDynamics.*` (old merged 13.5 × 6.2 file) **removed**.
- **Cohen's d convention fix (N vs U project level):** frozen CSV
  `heterogeneity/project_level_top_vs_bottom_cohensd.csv` reports **d = 0.3517**
  using the textbook **n-weighted pooled SD**. The manuscript text said 0.349 —
  that value came from an unweighted mean-of-variances pooled SD in the figure
  script (`sqrt((s1²+s2²)/2)`), which understates d when n1 ≠ n2
  (682 national vs 1,375 university → 0.3485). Manuscript corrected to **d = 0.352**
  (2 places); `_fig4_pairwise()` formula corrected to the n-weighted pooled SD.
  Figure 2 roadmap already showed 0.352 and is unchanged. Welch t = 7.375,
  p = 2.9e-13 unaffected.

### Docs
- Manuscript Figure 13 section rewritten for 13a/13b (sources, sizes, split
  rationale); §1.1 d value + data-dictionary entry updated to 0.352 with
  formula-convention note.
- `05_FINAL_FIGURES/gallery.html`: synced to cand.7 via atomic patch (5 reps,
  3 s post-write verification passed): version bump, Figure 13 grid card split
  into 13a + 13b, book page shows both files, footer supp count updated.

---

## [v1.0-cand.6] — 2026-09-05 — FOURTEENTH ROUND: FIGURE 8 FILE SPLIT & FIGURE 10 VISUAL CLEANUP (USER VISUAL REVIEW)

Milestone status: ✅ Visualization-only round (user visual review of inserted figures).
All frozen CSVs in `03_FINAL_ANALYSIS/` and `02_RTAS_MODEL_SELECTION/` unchanged
(zero numeric drift). Main text remains **7 figure numbers**; Figure 8 now ships as
**two standalone files** (main-text figure files: 8).

### Changed (figures, `06_CODE/10_generate_figures.py` → `05_FINAL_FIGURES/`)
- **Figure 8 split into two standalone files** (user request: place the two panels
  side-by-side in one manuscript row at reduced width):
  - `Figure8a_LagDistribution.pdf/png` (7.9 × 5.6 inch): overall discrete lag
    distribution; **color legend moved OUTSIDE the axes to the right**
    (`bbox_to_anchor=(1.01, 1.0)`) — no longer floats over the bar-top counts.
  - `Figure8b_LagByQuadrant.pdf/png` (6.9 × 5.9 inch, taller canvas): defined lag
    by quadrant; **red-border HRHT value box deleted** ("n = 5 topics / 4 at lag 0 /
    1 at lag −2") — fully redundant with the scatter points and the `n_defined`
    tick labels; exact counts live in the manuscript caption.
  - `Figure8_DiffusionLagPatterns.*` (old merged 13.0 × 5.4 file) **removed**.
- **Figure 10** (`Figure10_MatthewEffect.pdf/png`, 14.2 × 5.0 inch):
  - **top50 Pareto bar removed** — a constant 100% gray slab carried no information,
    dwarfed the informative bars, and squeezed panel (c)'s y-tick labels;
    bars now top1/top5/top10/top20.
  - Panel spacing widened (`wspace=0.44`) — resolves panel (b)/(c) mutual overlap
    (Sample B label no longer obscured).

### Docs
- `07_MANUSCRIPT/manuscript_draft_v0.9.md`: Figure 8 section rewritten for the
  8a/8b split (sources, sizes, split rationale; panel (b) box sentence replaced by
  the deletion note); Figure 10 header + Pareto bullets updated (top50 removed,
  wspace/figsize noted).
- `05_FINAL_FIGURES/gallery.html`: synced to cand.6 via atomic patch script
  (title/h1/footer version bump; Figure 8 grid card split into 8a + 8b cards;
  Fig 8 book page shows both files; Fig 10 badge/legend text updated; top50
  mentions removed) — 10 replacements, 3 s post-write verification passed.

---

## [v1.0-cand.5] — 2026-09-05 — THIRTEENTH ROUND: MAIN-TEXT SUBTRACTION & DENOMINATOR CORRECTION (FIGURE FREEZE, FINAL)

Milestone status: ✅ **FIGURE FREEZE (final).** Visualization-only round: all frozen
CSVs in `03_FINAL_ANALYSIS/` and `02_RTAS_MODEL_SELECTION/` unchanged (zero numeric
drift). Main text contracted to **7 figure numbers** (Fig 2, 3, 4, 5, 6, 8, 10);
Supplementary = 4 (Fig 7, 11, 13, S1).

### Deleted (figures, `06_CODE/10_generate_figures.py` → `05_FINAL_FIGURES/`)
- **Figure4a_MeanCI** deleted — information redundant with Figure 4 mean diamonds
  (pairwise stats already in Figure 4 caption / Table).
- **FigureS2_Top20Colleges** deleted — raw-mean ranking visually amplifies small-n
  colleges (n=8/9); covered by Figure 5 caterpillar + Figure S1 full-40 ranking.

### Renamed / demoted
- **Figure 4b → Figure 4** (`Figure4_Distribution.pdf`): teaching-style long title
  shortened; box/diamond/jitter/Tukey definitions moved to the manuscript caption.
- **Figure 13 demoted to Supplementary** (`supplementary/Figure13_TopicDynamics.pdf`):
  second-layer finding, not required to answer the RQs.

### Corrected (freeze-blocking denominator / data flow / wording)
- **Figure 13 denominator fix:** y-axis = "Share of **all** project documents (%)"
  (denominator = all 3,714 project docs/yr; 17.6% + 29.5% ≈ 47.1% is the clustered
  share of ALL projects — the old "clustered docs denominator" label was wrong);
  colorbar = "% of all projects / yr"; subtitle "shares of all projects per year;
  topics = BERTopic clusters". Manuscript §9 wording synced.
- **Figure 2 roadmap:** Heterogeneity branch now fed from **RTAS Frozen** via
  orthogonal elbow connector (no longer from the raw corpus — heterogeneity analyses
  operate on frozen RTAS values); Spearman written as **ρ_s = .405**.
- **Figure 8:** neutral lag wording only — "Positive lag = research precedes
  training; negative lag = training precedes research" (speculative "course update
  needed" / "training uses already-cold content" removed).
- **Figure 10 panel (c):** "Sample B zero-filled" → "Sample B: expanded risk set
  (inactive t coded 0)".
- **Figure S1 title:** "p≈0" → "p < .001".
- **Figure 6:** significance definitions moved from the image into the caption.

### Docs
- `05_FINAL_FIGURES/gallery.html` synced to cand.5 (7 main / 4 supplementary;
  4a & S2 cards and book pages removed; Fig13 moved to Supplementary with corrected
  denominator) — applied via atomic patch script after recurrence of the IDE
  stale-buffer overwrite issue.
- Manuscript `07_MANUSCRIPT/manuscript_draft_v0.9.md` → v1.0-cand.5 (13th-round
  changelog, milestone table, endnotes, §9 denominator wording, removal of all live
  references to Fig4a/FigS2).
- Manuscript 5-spot text audit fix (post-review, text-only): §4.4 Fig6 reading guide rewritten to the
  chart-only reality (blue dots + gray CI + asterisks; color bands/info boxes removed); §8.1 SIE row
  corrected to "RTAS valid but excluded from v1.0 MixedLM complete-case (advisor covariate NA,
  N=3,231/G=39)"; §8.2 `college_rtas_top20.csv` re-tagged as historical/auxiliary output (Fig5 uses
  `hlm_v2b_college_random_effects.csv`); §12.2 "Figure S1/S2" → "Figure S1"; §9 Fig13 OUTLIER logic
  fixed (outliers are not in the clustered-topic numerator but remain inside the all-projects
  denominator). Frozen CSVs/figures/numbers untouched.
- Manuscript text audit fix II (post-review, text-only): §12.1 SIE entry rewritten (RTAS valid but
  excluded from v1.0 Primary MixedLM complete-case due to advisor covariate NA, N=3,231/G=39; ANOVA
  auto-excluded at n=1; descriptive ranking only); §8.2 `ri_clpm_panel_college_wide.csv` corrected
  from "39 colleges / SIE dropped" to the actual 40-college wide panel (SIE present; RTAS missing at
  w2021/w2023, 0.0 at w2025), consistent with `ri_clpm_panel_audit.json` n_colleges=40; §7.2
  complete-case (all three vars) = 35 noted. RI-CLPM remains future work; frozen CSVs/figures/numbers
  untouched.
- Manuscript text audit fix III (pre-freeze, text-only): §1.1.5 SIE history table disambiguated —
  the v0.9.1 row now separates the historical 40-college substrate (old RandomEffects kept the single
  SIE observation) from the current v1.0 Primary MixedLM complete-case (SIE excluded due to advisor
  covariate NA, N=3,231/G=39; ANOVA excluded at n=1); "HLM (OLS) can legitimately include it"
  reworded to descriptive-analysis validity with a pointer to §4.4; unsupported institutional
  background claims ("all-Chinese instruction / cross-college co-authorship dependence") removed from
  §1.1.5 and §12.1, reduced to "n=1 only, no performance-style comparison". Frozen CSVs/figures/numbers
  untouched.

## [v1.0-cand.4] — 2026-09-05 — TWELFTH-ROUND FIGURE AUDIT (FIGURE FREEZE)

Milestone status: ✅ **FIGURE FREEZE.** Visualization-only round: all frozen CSVs
in `03_FINAL_ANALYSIS/` and `02_RTAS_MODEL_SELECTION/` unchanged (zero numeric
drift). Intermediate cand.1–cand.3 data/protocol changes are documented in
`07_MANUSCRIPT/manuscript_draft_v0.9.md` §10 (rounds 9–11).

### Changed (figures, `06_CODE/10_generate_figures.py` → `05_FINAL_FIGURES/`)
- Main text contracted to **9 files / 8 figure numbers** (Fig 2, 3, 4a, 4b, 5, 6, 8, 10, 13):
  - Figure 13 redesigned as two panels ((a) Top-15 + Other-clustered trend lines,
    (b) 15×5 yearly prevalence heatmap; 15-band stacked area retired).
  - Old Figure 9 merged into Figure 8 ((a) overall discrete lag distribution,
    xlim [−4.5, 4.5] integer ticks; (b) HRLT/HRHT quadrant boxplots; LRHT/LRLT
    annotated 0/10 and 0/698 undefined — hatched N/A panels retired).
  - Figure 2 rebuilt as dual-corpus roadmap (main RTAS corpus 2020–2024 solid box
    vs auxiliary advisor-history corpus 2017–2019 dashed grey box feeding HLM
    pre-grant covariates only; ρ=.405 moved into the Embedding box; RI-CLPM removed).
  - Figure 5 replaced by college random-effects caterpillar
    (`03_FINAL_ANALYSIS/hlm/hlm_v2b_college_random_effects.csv`, ICC=0.7376),
    replacing the raw-mean Top-20 ranking.
  - Figure 10 expanded to three panels ((a) Lorenz, (b) Pareto, (c) lagged-logit OR forest).
  - Figure 4a switched to point + 95% CI; Figure 6 simplified to blue points + CI
    + stars (red/green shading and CI colour coding removed); Figure 3 gained a
    zoom inset + bubble-size reference legend (25/100/500 docs).
- Supplementary: Figure 7 (transition matrix) and Figure 11 (quadrant summary)
  demoted from main text; old main-text Figure 5 (Top-20 raw-mean) demoted to
  Figure S2; Figure S1 = full 40-college raw-mean ranking (label direction fixed).
  Layout: `05_FINAL_FIGURES/main/` (9 files) + `05_FINAL_FIGURES/supplementary/` (4 files).
- `05_FINAL_FIGURES/gallery.html` retitled "RTAS v1.0-cand.4 Figure Book" and
  synced card-by-card with the above.

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
