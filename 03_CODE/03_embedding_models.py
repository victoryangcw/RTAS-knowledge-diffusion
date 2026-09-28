# -*- coding: utf-8 -*-
"""03_embedding_models.py — MiniLM (+ BGE-M3 when torch stable) title embeddings.
PROVENANCE:
  01_DATA/final_analysis/table5_project_dataset_n3714.csv (project titles)
  + 01_DATA/raw_private/OpenAlex_12K_first_batch.csv (paper titles)
    --(03_embedding_models.py, MiniLM L2-normalized)-->
  02_RTAS_MODEL_SELECTION/embeddings/minilm/proj_emb_minilm.npy
  02_RTAS_MODEL_SELECTION/embeddings/minilm/paper_emb_minilm.npy
  (analogous for bge_m3/ after torch DLL fix)
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print(f"[03_embedding_models] PLACEHOLDER. See existing working script at\n"
          f"  02_RTAS_MODEL_SELECTION/02_encode_minilm.py\n"
          f"This script will be merged from it in Stage 3.")
