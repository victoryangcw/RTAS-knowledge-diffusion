# -*- coding: utf-8 -*-
"""08_matthew_effect.py  —  Gini + Pareto + transition matrix + lagged path-dependence.
Canonical numbers (§5 of manuscript, config canonical_numbers):
  gini(national projects)=0.767, Top5% supervisors=97, Top5% national share=34.0%,
  transition-matrix diagonal 62-66% (n=736 consecutive advisor-year pairs).

v1.0-cand.2 CHANGE (reviewer P0-b) — WITHDRAWN cross-sectional logit:
  The v0.9 cross-sectional logistic regression "P(national) ~ Top5% supervisor
  indicator, OR=6.085, p=2.31e-65" was CIRCULAR: the Top5% indicator was defined by
  cumulative national-project count, so regressing national-project attainment on
  it produced a tautological odds ratio. It is withdrawn (manuscript §5.5).
  REPLACED by a lagged t-1 -> t path-dependence logistic model on the advisor-year
  panel (temporal precedence breaks the circularity):

    logit P(nat_{a,t} = 1) = b0 + b1 * nat_{a,t-1} + b2 * log(1+load_{a,t-1}) + year FE_t
    standard errors clustered by advisor;  nat_{a,t} = advisor a has >=1 national
    project in year t; load = number of projects advised in year t-1.

    Sample A (active in BOTH t-1 and t; primary):  n=736 advisor-year cells, 491 advisors
      P(nat_t | nat_{t-1}=1)=35.2%  vs P(nat_t | nat_{t-1}=0)=20.7%
      OR(nat_{t-1}) = 2.25, 95% CI [1.57, 3.22], clustered p = 1.0e-5
    Sample B (active in t-1; inactive t zero-filled; robustness): n=2,302 cells, 1,621 advisors
      P(nat_t | nat_{t-1}=1)=13.5% vs 6.2%; OR = 2.28, 95% CI [1.68, 3.09], p = 1.4e-7
  Outputs (frozen in private analysis repo):
    03_FINAL_ANALYSIS/matthew_effect/lagged_logit_national_path_dependence.csv
    .../lagged_logit_national_path_dependence_sampleB.csv
    .../lagged_persistence_crosstab.csv
    .../lagged_logit_audit.json
    (old logistic_national_vs_top5pct.csv retained but no longer cited; RETRACTED)

PROVENANCE:
  01_DATA/final_analysis/table5_project_dataset_n3714_full.csv
    (advisor, year, project level; grouped to advisor-year panel)
    --(lagged t-1->t logistic, cluster SE by advisor; plus Gini/Pareto on cumulative
       national counts, and 3-tercile activity transition matrix)-->
  03_FINAL_ANALYSIS/matthew_effect/  (see manuscript §5 for the full output list)
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print("[08_matthew_effect] PLACEHOLDER (public repo; dataset not released).")
    print("v1.0: circular cross-sectional OR=6.085 withdrawn; see docstring for the")
    print("      lagged path-dependence model (OR=2.25 [1.57,3.22], clustered p=1.0e-5).")
