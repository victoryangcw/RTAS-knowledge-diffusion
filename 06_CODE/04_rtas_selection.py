# -*- coding: utf-8 -*-
"""04_rtas_selection.py  —  RTAS variants + C1..C5 evaluation + pre-specified rule.
PROVENANCE:
  02_RTAS_MODEL_SELECTION/embeddings/{minilm,bge_m3}/*.npy
  02_RTAS_MODEL_SELECTION/paper_college_year_map.csv
  02_RTAS_MODEL_SELECTION/human_validation/150pairs_human_annotations.csv
    --(04_rtas_selection.py, composite rule 0.45*η² + 0.30*stab + 0.25*C3, top5% TK pref)-->
  02_RTAS_MODEL_SELECTION/project_rtas_all_variants_minilm.csv
  02_RTAS_MODEL_SELECTION/rtas_model_selection.csv
  02_RTAS_MODEL_SELECTION/PRIMARY_RTAS.json
  02_RTAS_MODEL_SELECTION/selection_report.md

✅ v0.2 decision frozen: Primary RTAS = rtas_mini_mean. Running this script again
must reproduce the same decision on the same inputs (seed 42, same datasets).
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print("[04_rtas_selection] PLACEHOLDER. Working copy pipeline scripts are in\n"
          "  02_RTAS_MODEL_SELECTION/01_paper_college_map.py → 06_verify.py (6 scripts).\n"
          "In Stage 3 we merge them into this single 04_rtas_selection.py entry point.")
