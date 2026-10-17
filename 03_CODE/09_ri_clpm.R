# 09_ri_clpm.R — Random-Intercept Cross-Lagged Panel Model (longitudinal direction)
#
# Panel construction key: supervisor_id × year.
# Aggregates per cell: papers_count, citations_mean, srtp_count, srtp_rtas_mean.
#
# ⚠️ LANGUAGE CAVEAT (enforced in text + caption):
#   This provides "cross-lagged / longitudinal directional evidence".
#   Do NOT claim strict causal identification.
#
# Outputs:
#   03_FINAL_ANALYSIS/ri_clpm/ri_clpm_panel.csv
#   03_FINAL_ANALYSIS/ri_clpm/ri_clpm_coefficients.csv   (beta, se, z, p, CI)
#   05_FINAL_FIGURES/main/Figure_RICLPM_Paths.pdf

library(yaml)
cfg <- yaml::read_yaml("00_README/final_config.yaml")
stopifnot(cfg$statistics$ri_clpm$model == "RI-CLPM")
message(sprintf("[09_ri_clpm.R] v%s seed=%s caveat=%s",
                cfg$version, cfg$random_seed,
                cfg$statistics$ri_clpm$language_caveat))
# TODO (Stage 3)
