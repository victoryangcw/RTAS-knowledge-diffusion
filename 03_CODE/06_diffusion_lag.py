# -*- coding: utf-8 -*-
"""06_diffusion_lag.py  —  Topic-by-topic knowledge-diffusion lags.
Definition: lag_topic = t_project − t_paper
where t_paper  = first year topic prevalence in papers > 1.5%
      t_project = first year topic prevalence in projects > 0.5%
PROVENANCE:
  03_FINAL_ANALYSIS/topic_model/doc_topic_assignments.csv
    --(06_diffusion_lag.py, thresholds final_config.yaml topic_model.diffusion_lag)-->
  03_FINAL_ANALYSIS/diffusion_lag/diffusion_lag_summary.csv
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print("[06_diffusion_lag] PLACEHOLDER.")
