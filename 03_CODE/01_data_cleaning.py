# -*- coding: utf-8 -*-
"""06_CODE/01_data_cleaning.py  —  Build the canonical project dataset.

PROVENANCE:
  D:\dachuang_outputs\SCI_最终投稿图表包\01_主论文图表_全中文\table5_regression_dataset_with_new_rtas.csv
    --(01_data_cleaning.py, uses final_config.yaml §canonical_numbers)-->
  01_DATA/final_analysis/table5_project_dataset_n3714.csv
    AND
  01_DATA/public_sample/table5_projects_deidentified_n3714.csv (relabeled colleges)
"""
import yaml, pandas as pd, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "00_README" / "final_config.yaml").read_text(encoding="utf-8"))
SEED = CFG["random_seed"]
# TODO implementation in Stage 3 (after v0.2, during downstream analysis freeze)
if __name__ == "__main__":
    print(f"[01_data_cleaning] PLACEHOLDER. target_n={CFG['canonical_numbers']['n_projects']}")
