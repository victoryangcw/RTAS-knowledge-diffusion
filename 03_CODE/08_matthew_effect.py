# -*- coding: utf-8 -*-
"""08_matthew_effect.py  —  Gini + transition matrix + logistic + Top5% tests.
Canonical numbers (§7 of protocol, config canonical_numbers):
  gini=0.767, Top5% supervisors=97, Top5% national project share=34.0%.
PROVENANCE:
  01_DATA/final_analysis/table5_project_dataset_n3714.csv (supervisor_id, year, project_level, cumulative national projects)
    --(08_matthew_effect.py, Top5% via 5% of 1940 = 97 supervisors)-->
  03_FINAL_ANALYSIS/matthew_effect/supervisor_gini.csv
  03_FINAL_ANALYSIS/matthew_effect/transition_matrix_year.csv
  03_FINAL_ANALYSIS/matthew_effect/logistic_project_level.csv
  03_FINAL_ANALYSIS/matthew_effect/top5pct_tests.csv  (t, MWU, Cohen's d)
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print("[08_matthew_effect] PLACEHOLDER.")
