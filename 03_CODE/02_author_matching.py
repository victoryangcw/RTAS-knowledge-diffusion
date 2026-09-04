# -*- coding: utf-8 -*-
"""02_author_matching.py  —  OpenAlex authors → college advisor pinyin match.
(Precise full-name pinyin; homonym collisions skipped.)
PROVENANCE:
  01_DATA/raw_private/*.csv (advisor records) + 01_DATA/raw_private/OpenAlex_12K_first_batch.csv
    --(02_author_matching.py)-->
  01_DATA/interim/author_to_college_lookup.csv
  02_RTAS_MODEL_SELECTION/paper_college_year_map.csv
"""
import yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "00_README" / "final_config.yaml").read_text(encoding="utf-8"))
if __name__ == "__main__":
    print(f"[02_author_matching] PLACEHOLDER. target_matched_pct="
          f"{CFG['data']['openalex_papers_matched_pct']}")
