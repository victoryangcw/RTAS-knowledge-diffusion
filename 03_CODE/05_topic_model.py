# -*- coding: utf-8 -*-
"""05_topic_model.py  —  Static BERTopic + 4-quadrant + Dynamic BERTopic (diffusion lag).
PROVENANCE:
  01_DATA/final_analysis/table5_project_dataset_n3714.csv (project titles)
  01_DATA/raw_private/OpenAlex_12K_first_batch.csv (paper titles)
    --(05_topic_model.py, params from final_config.yaml topic_model section)-->
  03_FINAL_ANALYSIS/topic_model/doc_topic_assignments.csv
  03_FINAL_ANALYSIS/topic_model/topic_info.csv
  03_FINAL_ANALYSIS/topic_model/quadrant_aggregate.csv
  03_FINAL_ANALYSIS/diffusion_lag/diffusion_lag_per_topic.csv
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print("[05_topic_model] PLACEHOLDER. Requires rtas_mini_mean column frozen (v0.2 ✅).")
