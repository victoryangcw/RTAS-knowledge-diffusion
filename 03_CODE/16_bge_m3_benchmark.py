# -*- coding: utf-8 -*-
"""16_bge_m3_benchmark.py — v1.0-cand.10 (SECONDARY robustness, CONDITIONAL on network)

Post-freeze embedding robustness: encode the 150-pair reference set with BGE-M3
and compare its human-validity performance (Spearman rho, AUC) against the
frozen MiniLM (+0.405 / AUC 0.880).

Scope: ONLY the 150 reference pairs are encoded (not the full 60k corpus), to
keep this a fast validity benchmark. If BGE-M3 matches or exceeds MiniLM, the
primary embedding choice is robust; if MiniLM clearly wins, that strengthens
the MiniLM selection. Either way MiniLM remains primary (frozen).

Exit codes:
  0 = benchmark completed
  2 = BGE-M3 unavailable (no network / model download failed) — skip gracefully
"""
import warnings; warnings.filterwarnings('ignore')
import sys, os
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

BASE = r'D:/dachuang_outputs/SCI_最终投稿图表包'
PROJ = r'D:/vc-task/RTAS_FINAL_PROJECT'
ANN = pd.read_csv(BASE + '/mytask/标注任务_150对_人工LLM混合_已标注.csv')
COS = pd.read_csv(PROJ + '/02_RTAS_MODEL_SELECTION/human_validation/robustness/150pairs_with_cos_mini.csv')
OUT = PROJ + '/02_RTAS_MODEL_SELECTION/human_validation/robustness'

df = ANN[['pair_id', 'project_title', 'paper_title', 'annotator1_score']].merge(
    COS[['pair_id', 'cos_mini']], on='pair_id').sort_values('pair_id').reset_index(drop=True)
y = df['annotator1_score'].astype(int).values
pos = y >= 2

try:
    from FlagEmbedding import BGEM3FlagModel
    print('[BGE] loading BGE-M3 (may download on first run, needs network)...')
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)
    print('[BGE] model loaded')
except Exception as e:
    print(f'[BGE] unavailable: {type(e).__name__}: {str(e)[:120]}')
    print('[BGE] SKIP — document as planned future robustness; MiniLM stays primary.')
    sys.exit(2)

proj_emb = model.encode(df['project_title'].tolist())['dense_vecs']
paper_emb = model.encode(df['paper_title'].tolist())['dense_vecs']
# L2 normalize
proj_n = proj_emb / np.linalg.norm(proj_emb, axis=1, keepdims=True)
paper_n = paper_emb / np.linalg.norm(paper_emb, axis=1, keepdims=True)
cos_bge = np.sum(proj_n * paper_n, axis=1)

rho_bge, p_bge = spearmanr(cos_bge, y)
order = np.argsort(cos_bge); ranks = np.empty(len(cos_bge)); ranks[order] = np.arange(1, len(cos_bge) + 1)
n_pos, n_neg = int(pos.sum()), int((~pos).sum())
auc = (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
r_pb = float(np.corrcoef(cos_bge, pos.astype(float))[0, 1])
rho_mini, _ = spearmanr(df['cos_mini'].values, y)

rows = [
    dict(embedding='MiniLM (frozen primary)', spearman_rho=rho_mini, auc_ge2_vs_1=0.880131, note='frozen C1 reference'),
    dict(embedding='BGE-M3 (post-freeze robustness)', spearman_rho=rho_bge, auc_ge2_vs_1=auc, note=f'spearman_p={p_bge:.3g}'),
]
res = pd.DataFrame(rows)
res.to_csv(OUT + '/bge_m3_benchmark.csv', index=False, encoding='utf-8-sig')
print()
print(res.to_string(index=False))
print(f'\n[done] wrote {OUT}/bge_m3_benchmark.csv')
