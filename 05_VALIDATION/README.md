# Validation artefacts (title-redacted)

This folder contains the score-level artefacts used to evaluate the embedding and rating layers. The public snapshot deliberately does **not** distribute the original project titles, article titles, or title-to-pair mapping for the validation samples.

## Public representation

- Project titles are represented by non-resolving placeholders such as `PAIR_001`.
- Article titles are represented by non-resolving placeholders such as `ARTICLE_001`.
- The public 150-pair annotation sheet omits project tier, article year, citation count, and free-text notes; these fields are not needed to reproduce the reported score-level statistics.
- Pair identifiers, ordinal ratings, and frozen similarity scores are retained so correlations, AUCs, inter-rater agreement, test–retest reliability, and the LLM/encoder comparisons can be recalculated from the score-only tables.
- The original text pairs and their mapping to public approval lists remain in the restricted data store. Text-dependent lexical or encoder reruns require authorized access to that source; placeholder strings must not be used as input text.

## Files

- `150pairs_human_annotations.csv`: pair IDs and human ratings; title fields are placeholders.
- `150pairs_with_cos_mini.csv`: reference human scores paired with frozen MiniLM cosine values.
- `robustness/150pairs_with_cos_mini_and_bge.csv`: score-only MiniLM/BGE-M3 comparison values; original text fields are placeholders.
- `150pairs_llm_second_rater.csv`: LLM scores, with no original title text or free-text rationales.
- `second_rater_50pairs_*.csv` and `retest_40pairs_*.csv`: title-redacted rating forms and scores for independent-rater and test–retest checks.
- `robustness/hard_pair_ratings_anonymized.csv`: post-freeze challenge-set ratings, with no original title text.
- `robustness/*_stats.csv` and `robustness/*_benchmark.csv`: aggregate validation summaries.

The public score tables preserve the numerical evidence reported in the manuscript without providing a direct or score-assisted link from validation scores back to a project title. As with any material previously made public, this cleanup cannot recall external copies, caches, or previously cloned repositories.
