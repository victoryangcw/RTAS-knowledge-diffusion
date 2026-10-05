# Validation artefacts (anonymized)

This folder contains the rating artefacts of the human/LLM validity program.
Two anonymization rules were applied before the repository was made public:

1. **Raters are pseudonymous.** The reference annotator is "Rater A"
   (annotator1) and the independent second rater is "Rater B"; personal names
   were removed from file names, row keys, and documentation across the whole
   repository and its git history.
2. **Project titles are replaced by pair IDs.** In all rating files the
   `project_title` column contains the placeholder `PAIR_<pair_id>` instead of
   the original Chinese project title. Paper titles (public OpenAlex metadata),
   project level/college, and all ratings are retained, so every inter-rater,
   LLM, and triangulation statistic in the paper remains independently
   checkable from these files. The title-to-pair mapping is held in the
   private data store.

Historical commits may still contain the original title strings; the current
tree is fully anonymized.

## Hard-pair challenge-set robustness

The post-freeze hard-pair validation is published in `robustness/` as:

- `hard_pair_ratings_anonymized.csv`: 174 anonymized project--article pairs with sampling stratum, MiniLM cosine, two human ratings, consensus score, and absolute rater difference.
- `compute_hardpair_stats.py`: recomputes inter-rater agreement, Spearman correlation, overall AUC, stratum-specific summaries, and the high-similarity-stratum bootstrap AUC interval.

The challenge set is deliberately enriched using MiniLM cosine strata and is therefore a robustness/challenge-set assessment rather than a population-validity sample. Project titles remain anonymized; no private title-to-pair mapping is distributed.

