# -*- coding: utf-8 -*-
"""07_hlm.py  —  Hierarchical Linear Model (2-level projects-within-colleges).
⚠️ SINGLE-SOURCE PROVENANCE RULE:
  This script writes EXACTLY ONE fitted-model serialisation + coefficients CSV.
  Both Table 6 (04_FINAL_TABLES/) AND Figure 6 (05_FINAL_FIGURES/) must be built
  from that CSV — never produce them independently. The current paper draft
  misaligns HLM variables between Table 6 and Figure 6; this rule prevents it.
PROVENANCE:
  01_DATA/final_analysis/table5_project_dataset_n3714.csv  (righthand-side vars + college)
  02_RTAS_MODEL_SELECTION/project_rtas_all_variants_minilm.csv  (primary_rtas_column)
    --(07_hlm.py, linearmodels.RandomEffects / lme4)-->
  03_FINAL_ANALYSIS/hlm/final_hlm_fit.pkl / .feather
  03_FINAL_ANALYSIS/hlm/hlm_coefficients.csv   → inputs to Table6 + Figure6
  03_FINAL_ANALYSIS/hlm/hlm_fit_summary.txt    (ICC, R², n_groups, n_obs)
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print("[07_hlm] PLACEHOLDER. Single-source rule implemented inside when filled.")
