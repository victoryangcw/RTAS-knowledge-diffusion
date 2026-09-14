# Measuring Research–Training Semantic Alignment: Project-Level Cross-Lingual Embeddings, Topic Prevalence Asymmetries, and Resource Concentration in Undergraduate Innovation Programs

**Submission clean version v1.0 (frozen from master manuscript v1.0-cand.13; all statistics from frozen CSVs in `03_FINAL_ANALYSIS/`)**
**Target journal: Scientometrics**

---

## Abstract

Universities increasingly expect undergraduate research-training programs to reflect the active research of their faculty, yet whether student project topics actually align with institutional research output is rarely measured at the project level. We propose the Research–Training Alignment Score (RTAS), a project-level, cross-lingual semantic alignment measure that computes the mean cosine similarity between the embedding of a student project title and the embeddings of the unique OpenAlex-indexed articles assigned to the same college through advisor–author name linkage. We apply RTAS to 3,714 undergraduate innovation projects (2020–2024) at a large comprehensive Chinese university and a corpus of 56,901 OpenAlex articles, of which 33,312 (58.5%) are assigned to 40 colleges. Embedding-level validity is supported by converging evidence for pairwise semantic validity and rating reliability: Spearman ρ = 0.405 (n = 150 human-rated title pairs; AUC = 0.880 for discriminating related from unrelated pairs), two independent human raters (quadratic-weighted κ = 0.465/0.606; inter-rater κ = 0.826), test–retest reliability (κ = 0.643), and an LLM second rater (κ = 0.459); naive lexical baselines perform substantially worse (ρ ≈ 0.30, AUC ≈ 0.64). Four findings emerge. (1) Project RTAS increases monotonically with funding level (university 0.1212, provincial 0.1391, national 0.1460; η² = 1.89%), but funding level shows no independent association with alignment once college random effects and advisor covariates are included. (2) Joint BERTopic modeling (60,615 documents; 886 non-outlier topics) reveals a marked prevalence asymmetry: 173 topics show high research-side but low project-side prevalence, whereas only 10 show the reverse. (3) Among the 24 lag-definable HRLT topics, the median lag was +0.5 years (50.0% research-first, 37.5% same-year first non-trivial presence, 12.5% project-first); the remaining five lag-definable topics are HRHT, while LRHT and LRLT have no definable lags under the frozen rule. (4) National project allocation is highly concentrated (Gini = 0.746; top 5% of advisors hold 31.0%) and strongly path-dependent (lagged logit OR = 2.06, 95% CI [1.53, 2.76]), yet top-advisor projects show no statistically distinguishable alignment advantage (d = +0.083, p = 0.065): resource concentration did not translate into a statistically distinguishable alignment advantage. In hierarchical models (ICC = 0.738), advisors' pre-project publication output is positively associated with alignment (β = +0.0043, p < 0.001), whereas prior supervisory load is negatively associated (β = −0.0063, p < 0.001), consistent with a capacity-dilution interpretation. RTAS indexes alignment, not training quality, and all estimates are observational.

**Keywords:** research–training alignment; undergraduate innovation; semantic similarity; multilingual sentence embeddings; BERTopic; hierarchical linear modeling; Matthew effect; Science and technology studies

---

## 1 Introduction

### 1.1 Motivation

Research universities worldwide have made the integration of research and teaching a central policy goal. China's National Undergraduate Innovation and Entrepreneurship Training Program (hereafter *undergraduate innovation projects*) funds student projects annually at three administrative levels—university, provincial, and national—under faculty supervision. A natural question for scientometrics is whether the topics students actually pursue align with the research their colleges are actively publishing, and how institutional mechanisms—funding level, advisor characteristics, and the concentration of supervisory resources—relate to that alignment.

Existing work on research–teaching relationships operates mostly at the level of individual scholars or institutions, using performance composites and indicator correlations (Maisano et al. 2023; Scafetta 2025). The scholar-level RT-score of Scafetta (2025), for example, combines research and teaching performance into a faculty-level index. What is missing is a project-level measure of *semantic* alignment: whether the content of a student project sits inside the college's actual research portfolio. Such a measure must bridge languages (Chinese project titles; English article titles) and scale to large numbers of titles.

### 1.2 This study

We introduce RTAS (Research–Training Alignment Score), defined for each project as the mean cosine similarity between the multilingual sentence embedding of its title and the embeddings of the unique articles assigned to its college through advisor–author linkage over a cumulative window. RTAS is deliberately *not* a performance ranking: it measures where student topics fall relative to the observed college research portfolio (an observable proxy for the research frontier), not novelty, leadership, or impact.

We ask four research questions about the 2020–2024 cohorts of one large comprehensive Chinese university (40 colleges):

- **RQ1 (Heterogeneity).** Does RTAS differ by project funding level, and does the difference survive college and advisor controls?
- **RQ2 (Topic asymmetries and diffusion lags).** How are research-side and project-side topic prevalence distributed across quadrants, and where annual onset is identifiable on both sides, what lags are observed?
- **RQ3 (Determinants).** How much RTAS variance lies between colleges, and which advisor and project characteristics are associated with alignment?
- **RQ4 (Concentration).** Is national project allocation concentrated and path-dependent across supervisors, and does concentration coincide with higher alignment?

A single-institution design is a deliberate choice: it holds the funding regime, governance, and time window constant while spanning 40 discipline organizations—a within-institution comparative setting for observing between-college variation—at the cost of external validity (Sect. 5).

### 1.3 Contributions

1. A reproducible, project-level, cross-lingual semantic alignment measure (RTAS) with an explicit validity program (human raters, test–retest, LLM second rater, lexical baselines) and frozen aggregation choice.
2. A static-prevalence quadrant decomposition of 886 research–training topics with threshold and clustering sensitivity checks, and a conservative, rule-based diffusion-lag analysis restricted to topics whose annual onset is definable on both sides.
3. Evidence that administrative funding level and resource concentration are decoupled from alignment: raw level differences are strongly attenuated after accounting for college and advisor context, and supervisory-resource concentration does not coincide with higher alignment.

---

## 2 Data and Methods

### 2.1 Data sources and corpus tiers

**Projects.** 3,714 undergraduate innovation projects approved in 2020–2024 at the case university (university-level 1,375, 37.0%; provincial 1,657, 44.6%; national 682, 18.4%), each with title (92% Chinese), level, year, college (40), and advisor(s). Multi-advisor fields were split using the same delimiter rules as in advisor-covariate construction, yielding 1,834 individual advisors and 4,244 advisor–project links (528 projects were co-supervised).

**Articles.** 56,901 articles (type=article, 2020–2024) retrieved from OpenAlex for institution I37461747 via cursor pagination, with 100% English titles; yearly distribution 9,970 / 10,117 / 12,002 / 11,954 / 12,858. An extended 2017–2019 pool (22,438 articles; total 79,339) serves *only* to compute advisors' pre-project publication windows and does not enter RTAS or topic modeling.

**Advisor–article linkage.** Advisor names are converted to pinyin keys (forward and reverse), matched against normalized OpenAlex author names with a college prior; ambiguous keys are skipped. 33,312 articles (58.5%) are assigned to colleges (mean 1.83 colleges per matched article); per project, advisor covariate status is matched (2,750), ambiguous (748), or unmatched (216), with unmatched covariates coded NA (not zero).

**Three corpus tiers (not interchangeable).** ① Retrieval corpus: 56,901 articles (full denominators for the article side of topic prevalence). ② Advisor-matched college portfolios: 33,312 articles—the only subset entering RTAS reference portfolios $P_{c,t}$. ③ Joint BERTopic corpus: 60,615 documents = 56,901 article titles + 3,714 project titles.

### 2.2 RTAS definition

For college $c$, year $t$, project $p$:

$$\text{RTAS}(p,c,t)=\frac{1}{|P_{c,t}|}\sum_{j\in P_{c,t}}\cos(\mathbf e_p,\mathbf e_j),$$

where $\mathbf e_p$ is the L2-normalized 384-dim embedding of the project title, and $P_{c,t}$ is the set of unique articles assigned to college $c$ over the cumulative window $[2020,t]$ via advisor–author linkage (a co-supervised article counts once; cross-college articles count once per college). Aggregation is the mean cosine. Titles-only is a design requirement, not a shortcut: project-side unstructured content does not exist in the original records, so the title is the only symmetric, cross-lingually comparable text unit on both sides; the cost (sparse semantics) is discussed in Sect. 5. "Research frontier" is operationalized as the *observed advisor-linked college research portfolio*—an observable proxy; RTAS does not measure novelty or influence (no citation or journal-tier information enters the score, except that advisor covariates use pre-project publication counts).

RTAS is distinct from scholar-level research–teaching composites such as the RT-score (Scafetta 2025) and from correlational studies of research and teaching indicators (Maisano et al. 2023): it is a project-level semantic alignment measure and is not used for performance ranking.

### 2.3 Embedding and aggregation choice

Embeddings use `paraphrase-multilingual-MiniLM-L12-v2` (384-dim), chosen for Chinese–English coverage, efficiency on 60,615 documents, and embedding-level validity (Sect. 2.4). Five aggregation variants (mean, top-5/10/20 mean, centroid) were compared under a pre-specified composite rule combining known-groups separation (η² of level ANOVA, weight 0.45), temporal stability (0.30), and topic-model K-stability (0.25). Mean aggregation wins (composite 0.742 vs 0.480 for the best top-K variant) and is frozen as Primary RTAS. Frozen RTAS descriptives: mean 0.1337, SD 0.0723, median 0.1362, range [−0.0575, 0.3960], N = 3,714 (no missing).

### 2.4 Validity program (converging evidence)

The protocols for the following validation checks were specified before execution; all were treated as secondary analyses and did not alter the frozen RTAS estimates.

- **Pairwise semantic validity (C1, embedding level).** On 150 human-rated project-title–article-title pairs (1–4 rubric), embedding cosine correlates with human relatedness at ρ = 0.405 (p = 2.6×10⁻⁷); bootstrap 95% CI [+0.281, +0.509]; permutation p < .001; Kendall τ-b = 0.327; leave-one-out max |Δρ| = 0.018. Binary discrimination of related (≥2) vs unrelated (=1): AUC = 0.880 [0.793, 0.949]. C1 is evidence of pairwise semantic validity, not a completed construct-validity certification; the small related-only subset (n = 16) is reported transparently (ρ = −0.253) with no inferential claim.
- **Inter-rater reliability.** Two independent, blind human raters scored a 50-pair subset: Rater A vs reference κ = 0.465 (exact agreement 72%); Rater B vs reference κ = 0.606 (78%; the reference rater's 46/50 ties at score 1 destabilize Spearman, so κ and agreement are interpreted); A–B κ = 0.826, ρ = 0.821, agreement 90%.
- **Test–retest.** Same reference rater, 40 reordered pairs after a ~12-day washout: κ = 0.643, ρ = 0.688 (p < .001), agreement 95%.
- **LLM second rater.** deepseek-reasoner (temperature 0, prompt v1.1), all 150 pairs blind: κ = 0.459, ρ = 0.638 (p < 10⁻¹⁸), agreement 93.3%. Triangulation against Rater B: ρ = 0.621, AUC = 0.932—above the frozen reference values, providing converging evidence; does not replace the frozen C1 estimates.
- **Naive lexical baselines.** Char 3–5-gram TF-IDF cosine, char-3-gram Jaccard, and BM25 Okapi applied directly to the Chinese–English pairs (no translation alignment; hence *naive* lexical baselines, structurally disadvantaged in this cross-lingual setting) reached ρ = 0.296–0.300 and AUC = 0.637–0.638 (TF-IDF: ρ = 0.300, AUC = 0.638; Jaccard: ρ = 0.296, AUC = 0.637; BM25: ρ = 0.298, AUC = 0.637), all below MiniLM's ρ = 0.405 / AUC = 0.880. The comparison supports multilingual semantic embedding over naive lexical overlap for the embedding choice; it makes no claim against translation-based or stronger cross-lingual methods.
- **Post-freeze encoder robustness.** As a post-freeze robustness check, the same 150 reference-rated title pairs were re-encoded with BGE-M3 (BAAI, 2024; 1024-dim multilingual dense embeddings) and compared with the frozen MiniLM encoder using paired bootstrap resampling (2,000 replicates; seed = 42). BGE-M3 yielded ρ = 0.334 and AUC = 0.811, compared with ρ = 0.405 and AUC = 0.880 for MiniLM. Paired bootstrap differences did not exclude zero for either Spearman correlation (Δρ = −0.071, 95% CI [−0.187, +0.036]) or AUC (ΔAUC = −0.069, 95% CI [−0.179, +0.032]). There was no evidence that BGE-M3 improved pairwise validity relative to the frozen MiniLM encoder, which was therefore retained as the primary encoder.

### 2.5 Topic modeling

BERTopic (UMAP → HDBSCAN → c-TF-IDF) is fit on the 60,615-document joint corpus with frozen parameters (random_state = 42). HDBSCAN yields 886 non-outlier topics plus a 38.47% outlier share—documents not assigned to any stable cluster under the frozen density-based parameters; quadrant and lag analyses are conditional on the 886 clustered topics (covering 61.53% of documents). Clustering-parameter sensitivity (min_cluster_size/min_samples = 15/7, 20/10, 8/3) leaves outlier rates stable (0.364–0.396) and the qualitative quadrant structure unchanged; topic counts vary with granularity (454–1,287), as expected.

### 2.6 Analysis windows

Each analysis uses the window its question requires, stated explicitly: RTAS uses the cumulative window [2020, t]; advisor covariates use the pre-project window [t−3, t−1] with year < t; diffusion lags use an annual first non-trivial presence rule (article side: some year with ≥3 articles and ≥0.2% of that year's articles, ≈ ≥20 articles/year at this corpus size; project side: ≥2 projects and ≥0.2%).

### 2.7 Statistical models

- **RQ1.** One-way ANOVA with Tukey HSD for familywise pairwise comparisons (Δ = higher − lower level); Welch pairwise tests are reported as supplementary checks. These comparisons are descriptive, not confirmatory, because the aggregation-selection composite already weighs level separation.
- **RQ2.** Quadrant classification by cumulative prevalence thresholds (article side: top-20% percentile = 0.0879% ≈ ≥50 articles; project side: fixed ≥0.500% ≈ ≥18.6 projects), with 15%/20%/25% sensitivity; diffusion lags only for topics meeting the Sect. 2.6 annual rule on both sides.
- **RQ3.** A two-level random-intercept mixed model was estimated using REML (`statsmodels MixedLM`), with projects nested within colleges (primary complete cases n = 3,231, 39 colleges; high-confidence-match sensitivity n = 2,750). Year was entered as a continuous variable centered at 2022. Fixed effects included provincial- and national-level indicators, log-transformed advisor pre-project three-year publication output, and log-transformed prior supervisory load (strictly year < focal year, mean across co-advisors). An unconditional means model gives the null ICC.
- **RQ4.** Gini and Pareto concentration of national projects across supervisors; a supervisor-year lagged logistic model P(nat_t) ~ nat_{t−1} + log(1+load_{t−1}) + year FE (categorical year fixed effects with 2021 as reference, because the earliest outcome year is t = 2021 given the t−1 lag; standard errors clustered by supervisor). Multi-advisor fields were split so that each distinct advisor–project pair was treated as one supervisory link (co-supervised projects contributed one link to each listed individual advisor); the analysis unit is the individual advisor (1,834). Main sample 979 supervisor-years, 627 advisors; robustness sample 2,469/1,560. This replaces a cross-sectional top-5% regression whose OR is constructively inflated by definition (top-5% membership is itself ranked on cumulative national projects).

All numbers derive from frozen CSVs under a fixed seed (42); no statistic was hand-edited.

---

## 3 Results

### 3.1 Funding level and alignment (RQ1)

Mean RTAS rises monotonically with level: university 0.1212, provincial 0.1391, national 0.1460. ANOVA F(2, 3711) = 35.72, p = 4.3×10⁻¹⁶, η² = 1.89% (95% bootstrap CI [1.14%, 2.86%]). Tukey HSD: P−U +0.0179***, N−U +0.0248***, N−P +0.0070 (p-adj = 0.082, ns); the largest pairwise gap (N−U) has Welch t = 7.375, p = 2.9×10⁻¹³, d = +0.352. The strict ordering is University < Provincial ≤ National. In the hierarchical model, however, provincial (β = +0.0006) and national (β = −0.0016) dummies are indistinguishable from zero (95% CIs cross 0): the raw level differences are attenuated to near zero after accounting for college and advisor context; administrative level itself has no independent association with alignment.

### 3.2 Static prevalence quadrants (RQ2, classification)

Classifying the 886 clustered topics by cumulative prevalence (Table 1):

| Quadrant | Meaning (pooled 2020–2024 static prevalence; no temporal content) | Topics | Articles | Projects |
|---|---|---|---|---|
| HRHT | high research-side, high project-side prevalence | 5 | 2,090 | 308 |
| HRLT | high research-side, low project-side prevalence | **173** | 18,141 | 399 |
| LRHT | low research-side, high project-side prevalence | 10 | 219 | 278 |
| LRLT | low on both sides | 698 | 15,097 | 765 |
| Total | | 886 | 35,547 | 1,750 |

(Quadrant sums fall short of corpus totals because outliers are outside the four quadrants.) HRLT dominates the high-research region: 173 topics with high article-side but low project-side prevalence—the largest prevalence mismatch block. LRHT comprises only 10 topics. Threshold sensitivity (article-side top-15%/20%/25%) leaves conclusions stable: HRLT 128/173/224 (always ≥92% of high-research topics), LRHT 10/10/8, HRHT 5/5/7, and the 29 lag-definable topics (Sect. 3.3) always fall in HRLT/HRHT. Quadrant labels carry no temporal meaning; temporal interpretation is admitted only in Sect. 3.3 for the 29 topics whose lags are defined.

### 3.3 Diffusion lags where definable (RQ2, temporal)

Under the annual first non-trivial presence rule, only 29 of 886 topics (3.27%) are definable on both sides—24 in HRLT, 5 in HRHT. Overall median lag is 0 years (mean +0.59). In HRLT, the median lag is +0.5 years (mean +0.79): 50.0% (12/24) of these topics show research-side presence first, 37.5% show same-year first non-trivial presence, and 12.5% show project-side presence first. LRHT (0/10) and LRLT (0/698) never reach the article-side annual threshold in any single year, so their lags are *undefined in this corpus*—an empirical fact (their low-research-side classification makes it highly likely, though not a logical identity), not missing data. Consequently, statements that training content "trails research" cannot be made for these strata here; a curriculum-syllabus audit is the appropriate future instrument.

### 3.4 College context and advisor associations (RQ3)

The unconditional means model gives ICC = 0.7523; the full random-intercept model yields ICC = 0.7376—about three quarters of RTAS variance lies between colleges. The marginal R² was 0.0075, whereas the conditional R² was 0.7395, indicating that the observed fixed effects explained relatively little variance compared with the substantial between-college component. Among the observed project-level covariates, the advisor measures show the clearest associations:

- Advisors' **pre-project 3-year publication output** is robustly and positively associated with alignment (β = +0.0043, p = 3.2×10⁻⁹); moving from 0 to 10 pre-project publications corresponds to ≈ +0.010 RTAS (≈ 0.14 SD).
- **Prior supervisory load** (pre-project cumulative supervised projects) is negatively associated (β = −0.0063, p = 1.9×10⁻⁵), consistent with a capacity-dilution interpretation.
- **Year** (centered at 2022, entered as a continuous variable) is positively associated with RTAS (β = +0.00313 per year, p < 0.001); funding-level indicators are null (Sect. 3.1).

All estimates are observational associations, not causal identification. The high-confidence-match sensitivity sample reproduces every sign and significance level. Because RTAS also responds to disciplinary specialization, portfolio breadth, and title-language conventions, college-level results are not interpreted as performance.

**Leave-advisor-out sensitivity.** Because focal advisors' own publications enter their college's reference portfolio, the advisor-publication coefficient could be partly mechanical. To test this, RTAS was recomputed after removing all articles authored by any focal advisor of each project from that project's college reference portfolio (leave-advisor-out RTAS), and the identical MixedLM v2b specification was re-fit on the same 3,231 complete cases. The advisor-publication coefficient attenuated by approximately 10.5% (from β = +0.00427 to β = +0.00382) but remained positive and statistically significant (p = 5.3×10⁻⁷; 95% CI [0.00233, 0.00531], excluding zero). ICC (0.738) and conditional R² (0.739) were virtually unchanged. Of the 3,714 projects, 2,081 (56%) had at least one advisor-authored paper removed (mean 7.97 papers removed; mean portfolio reduction 4.1%; no project's portfolio became empty). This attenuation is consistent with some contribution from mechanical self-overlap, but most of the observed association persisted under the leave-advisor-out construction.

### 3.5 Concentration and path dependence (RQ4)

National project allocation is extremely unequal: Gini = 0.746 across individual advisors (total-project Gini = 0.368), the top 5% (92 advisors) hold 31.0% of national projects, and the top 20% hold 71.9%. Supervisory activity was itself uneven: 44.6% of individual advisors supervised one observed project, whereas 18.8% supervised four or more. Allocation is also *reproduced year to year*: conditional on last-year load and year fixed effects, a supervisor with a national project at t−1 has ≈ 2.1× the odds of another one at t (OR = 2.06, 95% CI [1.53, 2.76], p = 1.5×10⁻⁶, SEs clustered by supervisor; robustness sample OR = 2.45 [1.91, 3.16], p = 3.2×10⁻¹²). Projects supervised by the top 5% of national-project recipients had slightly higher mean RTAS, but the difference was small and not statistically significant (d = +0.083, Welch p = 0.065): resource concentration did not translate into a statistically distinguishable alignment advantage. RTAS measures alignment, not training quality; interpreting it as quality would exceed its operationalization.

---

## 4 Discussion

Three patterns organize the findings. First, **structure outweighs status**: alignment is more strongly associated with college context and advisor research activity than with a project's administrative label. The monotone raw gradient across funding levels compresses to zero once college random effects and advisor covariates enter, and the largest concentration of national funding (top 5% of advisors, path-dependent OR ≈ 2.1–2.5) shows no statistically distinguishable alignment advantage. Together with the negative association for prior supervisory load, a capacity-dilution reading is plausible: projects supervised by advisors with greater pre-project research activity show higher research–training alignment, whereas greater prior supervisory load is negatively associated with alignment. Second, **asymmetry is the norm, lag is the exception**: 173 of 886 topics are prevalent in research but not in training, while only 10 invert that pattern; yet annual onset is definable for only 29 topics, 13 of which show same-year first non-trivial presence. Static prevalence asymmetry and temporal lag are different constructs, and conflating them—treating every HRLT topic as "delayed"—would overread the design; the present analyses keep them separate. Third, **measurement transparency is a feature**: the validity program (independent raters, test–retest, LLM second rater, naive lexical baselines) supports the embedding layer without claiming completed construct validity, and the quadrant and lag thresholds are reported with sensitivity analyses rather than presented as natural kinds.

For research policy, the results suggest that administrative funding tier is less strongly associated with alignment than college context and advisor research activity. For scientometrics, RTAS illustrates how multilingual sentence embeddings can turn administrative title records into an organizational alignment metric; the same pipeline applies wherever student project titles and institutional publication portfolios coexist. We note that the advisor-publication association may be partly inflated by shared bibliographic construction—advisors' own papers enter the college reference portfolio against which their projects are scored—but the leave-advisor-out sensitivity (Sect. 3.4) shows that the coefficient attenuated by approximately 10.5% after advisor-authored papers were removed, while most of the observed association persisted under that construction.

---

## 5 Limitations

1. **Titles-only sparsity.** Titles are the only symmetric cross-lingual unit, but they compress semantics; alignment is measured on title distributions, not full texts.
2. **Linkage coverage.** 58.5% of articles are advisor-matched to colleges; unmatched articles (mostly cases with missing affiliations or pinyin ambiguity) are excluded from college reference portfolios, and the direction of any resulting bias is uncertain. Author-level identity resolution (OpenAlex author IDs) remains future work.
3. **Single institution.** The within-institution comparative setting comes at the cost of external validity; replication at universities with different disciplinary layouts is required before generalization.
4. **Observational design.** All associations (including capacity dilution) are non-causal; a directional panel design (RI-CLPM) remains a future direction; non-overlapping annual waves are required for valid panel identification.
5. **Low lag definition rate.** Only 3.27% of topics admit lags; LRHT/LRLT lags are undefined in this corpus, so no "outdated training content" claim is possible here. A curriculum-syllabus text audit could help address this gap.
6. **Measure sensitivity.** College-level RTAS mixes organizational context with measure sensitivity to disciplinary specialization, portfolio breadth, title-language conventions, and heterogeneity; rankings are not performance judgments.
7. **Encoder scope.** A post-freeze robustness check benchmarked BGE-M3 against MiniLM on the 150 reference pairs (Sect. 2.4); no significant improvement was found and MiniLM remains the primary (frozen) encoder. The present study did not re-run the full RTAS pipeline under an alternative encoder; a pipeline-v2 robustness under BGE-M3 remains future work.
8. **Granularity.** K = 886 is corpus-determined (HDBSCAN), not a theoretical granularity; K itself is not interpretable as a statistic.

---

## 6 Conclusion

We introduced RTAS, a project-level, cross-lingual semantic alignment measure, and applied it to 3,714 undergraduate innovation projects and 56,901 articles at one comprehensive university. Alignment rises with project funding level in raw comparisons but shows no independent association with level once college context and advisor research activity are modeled. Research-side and project-side topic prevalence are markedly asymmetric (173 high-research/low-project vs 10 low-research/high-project topics), and temporal lags are definable for only 29 topics. Of these, 24 fall in the high-research/low-project stratum, within which the median lag is +0.5 years. National project allocation is highly concentrated and path-dependent, yet concentration does not accompany higher alignment; advisors' pre-project research activity is positively associated with alignment and prior supervisory load is negatively so, consistent with capacity dilution. The alignment infrastructure—frozen embeddings, pre-specified validity checks, sensitivity-audited thresholds—prioritizes reproducibility over narrative convenience, and the measure indexes alignment, not quality.

---

## Declarations

**Funding.** [To be completed.]

**Conflicts of interest.** The authors declare no competing interests.

**Ethics approval.** The study analyzes administrative records and publicly retrievable bibliographic metadata. Institutional ethics/IRB determination is pending confirmation.

**Data availability.** (i) *Publicly retrievable layer:* OpenAlex article records are publicly retrievable through the documented institutional query (institution I37461747, type=article, 2020–2024, cursor pagination). (ii) *Restricted layer:* institutional undergraduate project records contain personal information (advisor names) and cannot be publicly redistributed; their acquisition and field structure are described in Methods. (iii) *Derived outputs:* all non-identifying derived outputs and code (frozen aggregation tables, quadrant and lag summaries, model estimates, and figure scripts) are available via the project repository (https://github.com/victoryangcw/RTAS-knowledge-diffusion), currently private and to be made public upon acceptance; the frozen seed (42) and frozen embeddings allow exact re-runs given equivalent inputs.

**Code availability.** See Data availability (iii); all analyses are scripted end-to-end from frozen CSVs.

**Author contributions.** [To be completed.]

---

## Figure list (files generated by `06_CODE/10_generate_figures.py` from frozen CSVs)

### Main text

| Fig. | Content | File |
|---|---|---|
| 1 | Technical roadmap (dual-corpus; 33,312 college-assigned papers in RTAS reference portfolios) | `main/Figure2_Roadmap` |
| 2 | Four-quadrant scatter, 886 topics (zoom inset; bubble-size legend) | `main/Figure3_QuadrantScatter` |
| 3 | Per-project RTAS by funding level (box + jitter; University-/Provincial-/National-level) | `main/Figure4_Distribution` |
| 4 | College random-effects caterpillar (BLUP ± 95% CI) | `main/Figure5_CollegeCaterpillar` |
| 5 | HLM coefficient forest plot (v2b) | `main/Figure6_HLM_Forest` |
| 6 | Diffusion-lag patterns, vertically stacked: (a) distribution of defined topic lags; (b) defined lag by quadrant (HRLT/HRHT) | `main/Figure8_DiffusionLag_Stacked` |
| 7 | Matthew effect: Lorenz, Pareto, lagged path-dependence OR | `main/Figure10_MatthewEffect` |

### Supplementary

| Fig. | Content | File |
|---|---|---|
| S1 | Supervisor transition matrix | `supplementary/Figure7_TransitionMatrix` |
| S2 | Four-quadrant summary bars (clustered-only denominators) | `supplementary/Figure11_QuadrantSummary` |
| S3a | Topic dynamics in undergraduate innovation projects (trend) | `supplementary/Figure13a_TopicTrend` |
| S3b | Top-15 topic prevalence heatmap | `supplementary/Figure13b_TopicHeatmap` |
| S4 | College RTAS full ranking (all 40) | `supplementary/FigureS1_CollegeRTAS_Full40` |

## Table list

- **Table 1** Static prevalence quadrants (Sect. 3.2; in text)
- **Table 2** Aggregation-variant selection composite (Sect. 2.3; to be typeset from `02_RTAS_MODEL_SELECTION/rtas_model_selection.csv`)
- **Table 3** HLM v2b estimates with 95% CIs (to be typeset from `hlm_mixedlm_v2b_primary_coefficients.csv`)
- **Table 4** Validity summary (C1, raters, test–retest, LLM second rater, baselines; to be typeset from `02_RTAS_MODEL_SELECTION/human_validation/robustness/*.csv`)

---

## References (to be completed at typesetting)

- Maisano, D. A., et al. (2023). *Scientometrics*. [Empirical relationships between research and teaching indicators.]
- Scafetta, N. (2025). *Scientometrics*. [Scholar-level RT-score.]
- Devlin et al. / Reimers & Gurevych (2019). Sentence-BERT.
- McInnes et al. (2018). UMAP.
- Campello et al. (2013). HDBSCAN.
- Grootendorst (2022). BERTopic.
- Nakagawa & Schielzeth (2013). R² for mixed models.
- [Full reference list to be compiled from the master manuscript's citation ledger.]
