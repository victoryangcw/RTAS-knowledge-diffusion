# -*- coding: utf-8 -*-
"""03_embedding_models.py — canonical embedding protocol (documentation only).

This file DOCUMENTS the exact protocol that produced the frozen embedding
vectors used by every RTAS computation in this repository. The vectors and
the raw corpus are not redistributed (see README, "What this repo does NOT
contain"), so this script is not runnable here; it exists so the encoding
step is fully specified rather than a black box.

CANONICAL PROTOCOL (v2 full-corpus freeze)
------------------------------------------
Encoder : sentence-transformers `paraphrase-multilingual-MiniLM-L12-v2`
          (384-dimensional, multilingual; cited in the manuscript as
          "MiniLM-L12-v2 (384-dimensional)")
Inputs  : project titles — frozen `table5_project_dataset_n3714.csv`
          paper titles   — private 56,901-record OpenAlex export
          (WHU, type=article, 2020-2024); titles taken as `str(title)`,
          empty titles encoded as ""
Call    : model.encode(titles, batch_size=128, normalize_embeddings=True)
          -> cast to float32
Outputs : 02_RTAS_MODEL_SELECTION/embeddings/minilm/paper_emb_minilm_full.npy
          (56,901 x 384, row order = raw paper CSV row order)
          02_RTAS_MODEL_SELECTION/embeddings/minilm/proj_emb_minilm.npy
          (3,714 x 384, row order = frozen project table row order)

Downstream: RTAS_i = mean cosine(project_i, cumulative [2020, t_i] college
portfolio). The provenance audit (19_numerical_provenance_audit.py) rebuilds
all 3,714 RTAS values from these vectors and verifies row alignment and the
frozen values to float32 precision (max |delta| 3.46e-08; see
06_RESULTS/19_numerical_provenance_ledger.csv).

A separate robustness benchmark re-encodes the 150 validation pairs with
BGE-M3 (16_bge_m3_benchmark.py); it does not feed the frozen RTAS.

NOTE: an early v0.2 script of the same name encoded the superseded
12,000-paper first batch; those vectors (`rtas_freeze/paper_emb_mini.npy`)
are historical and are NOT the numerical source of truth.
"""
from pathlib import Path

if __name__ == "__main__":
    print(__doc__)
