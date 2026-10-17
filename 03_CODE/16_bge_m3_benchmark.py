# -*- coding: utf-8 -*-
"""16_bge_m3_benchmark.py — v1.0-cand.13 (SECONDARY robustness, CONDITIONAL on network)

Post-freeze embedding robustness: encode the 150-pair reference set with BGE-M3
and compare its human-validity performance (Spearman rho, AUC) against the
frozen MiniLM (+0.405 / AUC 0.880), with PAIRED BOOTSTRAP for Delta-rho and
Delta-AUC.

Decision rule (pre-registered):
  - If BGE-M3 is similar to or only slightly better than MiniLM
    (Delta-rho CI includes 0 or is marginally positive) => robustness
    benchmark; MiniLM stays primary. This is a *good* result: RTAS does
    not depend on a specific encoder.
  - If BGE-M3 is clearly and stably better on BOTH rho and AUC
    (Delta CIs exclude 0, P(Delta>0) > 0.975) => discuss upgrading
    to BGE-M3 as primary in a pipeline v2.

Scope: ONLY the 150 reference pairs are encoded (not the full 60k corpus), to
keep this a fast validity benchmark. Either way MiniLM remains primary (frozen)
unless an explicit pipeline v2 is launched.

Exit codes:
  0 = benchmark completed
  2 = BGE-M3 unavailable (no network / model download failed) — skip gracefully
"""
import warnings; warnings.filterwarnings('ignore')
import sys, os, json
# IMPORTANT: torch MUST be imported before numpy/scipy/pandas on this Windows
# setup, otherwise c10.dll fails to initialize (DLL load order conflict).
import torch  # noqa: F401  — imported first to fix DLL loading
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, rankdata

BASE = r'D:/dachuang_outputs/SCI_最终投稿图表包'
PROJ = r'D:/vc-task/RTAS_FINAL_PROJECT'
ANN = pd.read_csv(BASE + '/mytask/标注任务_150对_人工LLM混合_已标注.csv')
COS = pd.read_csv(PROJ + '/02_RTAS_MODEL_SELECTION/human_validation/robustness/150pairs_with_cos_mini.csv')
OUT = PROJ + '/02_RTAS_MODEL_SELECTION/human_validation/robustness'
N_BOOT = 2000
SEED = 42

df = ANN[['pair_id', 'project_title', 'paper_title', 'annotator1_score']].merge(
    COS[['pair_id', 'cos_mini']], on='pair_id').sort_values('pair_id').reset_index(drop=True)
n = len(df)
y = df['annotator1_score'].astype(int).values
pos = y >= 2
cos_mini = df['cos_mini'].values


# ---------- metric helpers ----------
def metrics(x, y, pos):
    """Spearman rho + rank-based AUC + point-biserial r."""
    rho, p = spearmanr(x, y)
    ranks = rankdata(x)  # average ranks for ties
    n_pos = int(pos.sum())
    n_neg = int((~pos).sum())
    auc = (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg) if n_pos and n_neg else np.nan
    r_pb = float(np.corrcoef(x, pos.astype(float))[0, 1])
    return rho, auc, r_pb, p


# ---------- MiniLM reference ----------
rho_mini, auc_mini, rpb_mini, p_mini = metrics(cos_mini, y, pos)
print(f'[ref] MiniLM:  rho={rho_mini:+.4f}  AUC={auc_mini:.4f}  r_pb={rpb_mini:+.4f}  (p={p_mini:.4g})')


# ---------- load BGE-M3 ----------
try:
    from FlagEmbedding import BGEM3FlagModel
    print('[BGE] loading BGE-M3 (may download on first run, needs network)...')
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)
    print('[BGE] model loaded')
except Exception as e:
    print(f'[BGE] unavailable: {type(e).__name__}: {str(e)[:200]}')
    print('[BGE] SKIP — document as planned future robustness; MiniLM stays primary.')
    sys.exit(2)

# ---------- encode 150 pairs ----------
print('[BGE] encoding 150 project titles...')
proj_emb = model.encode(df['project_title'].tolist())['dense_vecs']
print('[BGE] encoding 150 paper titles...')
paper_emb = model.encode(df['paper_title'].tolist())['dense_vecs']
proj_n = proj_emb / np.linalg.norm(proj_emb, axis=1, keepdims=True)
paper_n = paper_emb / np.linalg.norm(paper_emb, axis=1, keepdims=True)
cos_bge = np.sum(proj_n * paper_n, axis=1)

rho_bge, auc_bge, rpb_bge, p_bge = metrics(cos_bge, y, pos)
print(f'[BGE] BGE-M3:  rho={rho_bge:+.4f}  AUC={auc_bge:.4f}  r_pb={rpb_bge:+.4f}  (p={p_bge:.4g})')

# ---------- paired bootstrap ----------
print(f'\n[boot] paired bootstrap: N_BOOT={N_BOOT}, seed={SEED}')
rng = np.random.RandomState(SEED)
boot_drho = np.zeros(N_BOOT)
boot_dauc = np.zeros(N_BOOT)
fail = 0
for b in range(N_BOOT):
    idx = rng.randint(0, n, size=n)
    xb = cos_bge[idx]
    xm = cos_mini[idx]
    yb = y[idx]
    pb = pos[idx]
    # skip degenerate bootstrap samples (all same class)
    if pb.sum() == 0 or pb.sum() == n:
        fail += 1
        boot_drho[b] = np.nan
        boot_dauc[b] = np.nan
        continue
    rb, ab, _, _ = metrics(xb, yb, pb)
    rm, am, _, _ = metrics(xm, yb, pb)
    boot_drho[b] = rb - rm
    boot_dauc[b] = ab - am

valid = ~np.isnan(boot_drho)
boot_drho = boot_drho[valid]
boot_dauc = boot_dauc[valid]
n_valid = len(boot_drho)

drho_mean = float(np.mean(boot_drho))
drho_lo, drho_hi = np.percentile(boot_drho, [2.5, 97.5])
drho_p_pos = float(np.mean(boot_drho > 0))

dauc_mean = float(np.mean(boot_dauc))
dauc_lo, dauc_hi = np.percentile(boot_dauc, [2.5, 97.5])
dauc_p_pos = float(np.mean(boot_dauc > 0))

print(f'[boot] valid bootstrap samples: {n_valid}/{N_BOOT}  (skipped {fail} degenerate)')
print(f'[boot] Delta-rho: mean={drho_mean:+.4f}  95%CI=[{drho_lo:+.4f}, {drho_hi:+.4f}]  P(Delta>0)={drho_p_pos:.3f}')
print(f'[boot] Delta-AUC: mean={dauc_mean:+.4f}  95%CI=[{dauc_lo:+.4f}, {dauc_hi:+.4f}]  P(Delta>0)={dauc_p_pos:.3f}')

# ---------- decision ----------
bge_better_rho = drho_lo > 0 and drho_p_pos > 0.975
bge_better_auc = dauc_lo > 0 and dauc_p_pos > 0.975
if bge_better_rho and bge_better_auc:
    decision = 'BGE-M3 clearly better on BOTH metrics — consider pipeline v2 upgrade'
elif drho_hi < 0 or dauc_hi < 0:
    decision = 'MiniLM clearly better — primary choice strengthened'
else:
    decision = 'BGE-M3 comparable to MiniLM — robustness evidence; MiniLM stays primary'

print(f'\n[decision] {decision}')

# ---------- save summary ----------
rows = [
    dict(embedding='MiniLM (frozen primary)', spearman_rho=rho_mini, auc_ge2_vs_1=auc_mini,
         pointbiserial_r=rpb_mini, spearman_p=p_mini, n=n),
    dict(embedding='BGE-M3 (post-freeze robustness)', spearman_rho=rho_bge, auc_ge2_vs_1=auc_bge,
         pointbiserial_r=rpb_bge, spearman_p=p_bge, n=n),
]
res = pd.DataFrame(rows)
res.to_csv(OUT + '/bge_m3_benchmark.csv', index=False, encoding='utf-8-sig')

# ---------- save per-pair cosine + human rating + binary label ----------
# Enables independent paired comparison and re-analysis without re-running BGE.
pair_df = pd.DataFrame({
    'pair_id': df['pair_id'].values,
    'project_title': df['project_title'].values,
    'paper_title': df['paper_title'].values,
    'human_score': y,                          # 1-4 ordinal reference rating
    'binary_label_ge2': pos.astype(int),       # 1 if rating >= 2 else 0
    'cos_mini': cos_mini,                       # frozen MiniLM cosine (primary)
    'cos_bge_m3': cos_bge,                      # BGE-M3 cosine (robustness)
})
pair_df['delta_cos_bge_minus_mini'] = pair_df['cos_bge_m3'] - pair_df['cos_mini']
pair_path = OUT + '/150pairs_with_cos_mini_and_bge.csv'
pair_df.to_csv(pair_path, index=False, encoding='utf-8-sig')

# ---------- save bootstrap results ----------
boot_res = {
    'n_boot': N_BOOT,
    'n_valid': int(n_valid),
    'n_degenerate': fail,
    'seed': SEED,
    'delta_rho': {'mean': drho_mean, 'ci95_lo': float(drho_lo), 'ci95_hi': float(drho_hi),
                  'p_delta_positive': drho_p_pos},
    'delta_auc': {'mean': dauc_mean, 'ci95_lo': float(dauc_lo), 'ci95_hi': float(dauc_hi),
                  'p_delta_positive': dauc_p_pos},
    'decision': decision,
}
with open(OUT + '/bge_m3_paired_bootstrap.json', 'w', encoding='utf-8') as f:
    json.dump(boot_res, f, indent=2, ensure_ascii=False)

print(f'\n{"="*60}')
print(res.to_string(index=False))
print(f'\n{"="*60}')
print(f'[done] wrote {OUT}/bge_m3_benchmark.csv')
print(f'[done] wrote {OUT}/bge_m3_paired_bootstrap.json')
print(f'[done] wrote {pair_path}  (per-pair cosines + labels)')
