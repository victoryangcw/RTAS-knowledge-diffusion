# -*- coding: utf-8 -*-
"""11_validation_robustness.py — v1.0-cand.9 (SECONDARY/ROBUSTNESS, not part of the frozen chain)

Robustness statistics for the 150-pair single-rater construct-validity check
(frozen point estimate: Spearman rho = +0.405, MiniLM embedding-level cosine).

Replicates the exact C1 pipeline of 02_RTAS_MODEL_SELECTION/04_evaluate.py
(title-exact index match, normalized-embedding dot product), then adds:
  R1 Spearman + bootstrap 95% CI        (seed 42, B=10,000 pair resamples)
  R2 Kendall tau-b + bootstrap 95% CI
  R3 Permutation p for Spearman         (seed 42, 10,000 sign-permuted ratings)
  R4 Dichotomized validity: rating >=2 vs =1 -> AUC(cos) + bootstrap CI,
     point-biserial r_pb                (addresses 134/150 ties at score 1)
  R5 Sensitivity: Spearman on the informative subset (score >=2, n=16) —
     reported for transparency only, n too small for inference
  R6 Leave-one-out influence: max |delta rho| and top-3 influential pairs

Outputs (new files only; NO frozen file is touched):
  02_RTAS_MODEL_SELECTION/human_validation/robustness/validation_robustness_stats.csv
  02_RTAS_MODEL_SELECTION/human_validation/robustness/150pairs_with_cos_mini.csv
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, kendalltau, mannwhitneyu

SEED = 42
B = 10_000
rng = np.random.default_rng(SEED)

BASE = Path(r'D:/dachuang_outputs/SCI_最终投稿图表包')
OUT = BASE / 'mytask' / 'rtas_freeze'
PROJ = Path(r'D:/vc-task/RTAS_FINAL_PROJECT')
DEST = PROJ / '02_RTAS_MODEL_SELECTION' / 'human_validation' / 'robustness'
DEST.mkdir(parents=True, exist_ok=True)

# ---- replicate 04_evaluate.py C1 pipeline (frozen inputs, read-only) ----
T5 = pd.read_csv(BASE / '01_主论文图表_全中文' / 'table5_regression_dataset_with_new_rtas.csv')
PA = pd.read_csv(r'D:/大创研究/论文最新进展/武汉大学_OpenAlex论文逐篇数据_2020_2024_首批.csv')
ANN = pd.read_csv(BASE / 'mytask' / '标注任务_150对_人工LLM混合_已标注.csv')
emb_p = np.load(OUT / 'paper_emb_mini.npy')
emb_r = np.load(OUT / 'proj_emb_mini.npy')

PT = T5['project_title'].fillna('').astype(str).tolist()
PA_TITLE = PA['title'].fillna('').astype(str).tolist()
proj_idx = {t: i for i, t in enumerate(PT)}
paper_idx = {t: i for i, t in enumerate(PA_TITLE)}

ann = ANN.copy()
ann['proj_i'] = ann['project_title'].map(proj_idx)
ann['paper_i'] = ann['paper_title'].map(paper_idx)
n_both = ann.dropna(subset=['proj_i', 'paper_i']).shape[0]

def cos(row):
    if pd.isna(row['proj_i']) or pd.isna(row['paper_i']):
        return np.nan
    return float(emb_r[int(row['proj_i'])] @ emb_p[int(row['paper_i'])])

ann['cos_mini'] = ann.apply(cos, axis=1)
sub = ann[['pair_id', 'annotator1_score', 'cos_mini']].apply(pd.to_numeric, errors='coerce').dropna()
sub = sub.sort_values('pair_id').reset_index(drop=True)
x = sub['cos_mini'].to_numpy(float)
y = sub['annotator1_score'].to_numpy(float)
n = len(sub)

# sanity check against frozen C1
rho_frozen, p_frozen = spearmanr(x, y)
print(f'[check] matched pairs with cos = {n}/150 (lookup both={n_both})')
print(f'[check] Spearman rho = {rho_frozen:+.4f} (frozen C1 human Spearman = +0.405; must match)')

def sp(a, b):
    return spearmanr(a, b)[0]

# ---- R1/R2 bootstrap CIs (pair resampling) ----
bo_sp, bo_kt = [], []
for _ in range(B):
    ii = rng.integers(0, n, n)
    xb, yb = x[ii], y[ii]
    if pd.Series(yb).nunique() < 2 or pd.Series(xb).nunique() < 2:
        continue
    bo_sp.append(sp(xb, yb))
    bo_kt.append(kendalltau(xb, yb, variant='b')[0])
ci_sp = (np.nanpercentile(bo_sp, 2.5), np.nanpercentile(bo_sp, 97.5))
ci_kt = (np.nanpercentile(bo_kt, 2.5), np.nanpercentile(bo_kt, 97.5))
tau = kendalltau(x, y, variant='b')[0]

# ---- R3 permutation p (permute ratings) ----
perm = []
for _ in range(B):
    perm.append(sp(x, y[rng.permutation(n)]))
perm_p = (np.sum(np.abs(perm) >= abs(rho_frozen)) + 1) / (B + 1)

# ---- R4 dichotomized (rating >=2 vs =1) ----
pos = y >= 2
n_pos, n_neg = int(pos.sum()), int((~pos).sum())
u = mannwhitneyu(x[pos], x[~pos], alternative='greater').statistic
auc = u / (n_pos * n_neg)
bo_auc = []
for _ in range(B):
    ii = rng.integers(0, n, n)
    yb, xb = y[ii], x[ii]
    pb, nb = int((yb >= 2).sum()), int((yb == 1).sum())
    if pb == 0 or nb == 0:
        continue
    bo_auc.append(mannwhitneyu(xb[yb >= 2], xb[yb == 1], alternative='greater').statistic / (pb * nb))
ci_auc = (np.nanpercentile(bo_auc, 2.5), np.nanpercentile(bo_auc, 97.5))
# point-biserial ( Pearson between cos and binary indicator )
r_pb = np.corrcoef(x, pos.astype(float))[0, 1]

# ---- R5 informative subset (score >=2) ----
rho_hi = sp(x[pos], y[pos]) if n_pos > 3 else np.nan

# ---- R6 leave-one-out influence ----
loo = np.empty(n)
for i in range(n):
    m = np.ones(n, bool); m[i] = False
    loo[i] = abs(rho_frozen - sp(x[m], y[m]))
top3 = sub.iloc[np.argsort(-loo)[:3]][['pair_id', 'annotator1_score', 'cos_mini']]

rows = [
    ('n_pairs_with_cos',        n,                    'of 150; exact-title match'),
    ('spearman_rho',            rho_frozen,           'frozen C1 point estimate (must equal +0.405)'),
    ('spearman_p_asymptotic',   p_frozen,             'asymptotic p (SciPy)'),
    ('spearman_p_permutation',  perm_p,               f'R3: permutation p, B={B}, seed={SEED}'),
    ('spearman_ci_low',         ci_sp[0],             f'R1: bootstrap 95% CI, B={B}, seed={SEED}'),
    ('spearman_ci_high',        ci_sp[1],             'R1'),
    ('kendall_tau_b',           tau,                  'R2'),
    ('kendall_ci_low',          ci_kt[0],             'R2 bootstrap 95% CI'),
    ('kendall_ci_high',         ci_kt[1],             'R2'),
    ('n_relevant_ge2',          n_pos,                'R4: rating >= 2'),
    ('n_irrelevant_eq1',        n_neg,                'R4: rating = 1'),
    ('auc_cos_ge2_vs_1',        auc,                  'R4: AUC of cos for rating>=2 vs =1'),
    ('auc_ci_low',              ci_auc[0],            'R4 bootstrap 95% CI'),
    ('auc_ci_high',             ci_auc[1],            'R4'),
    ('pointbiserial_r',         r_pb,                 'R4: Pearson(cos, 1[rating>=2])'),
    ('spearman_subset_ge2',     rho_hi,               f'R5: informative subset only (n={n_pos}); n too small for inference'),
    ('loo_max_abs_drho',        float(np.nanmax(loo)), 'R6: max |delta rho| leaving one pair out'),
]
out = pd.DataFrame(rows, columns=['stat', 'value', 'note'])
out.to_csv(DEST / 'validation_robustness_stats.csv', index=False, encoding='utf-8-sig')

per_pair = sub.rename(columns={'annotator1_score': 'human_score'})
per_pair.to_csv(DEST / '150pairs_with_cos_mini.csv', index=False, encoding='utf-8-sig')

print()
print(out.to_string(index=False))
print()
print('[R6] top-3 influential pairs:')
print(top3.to_string(index=False))
print()
print(f'[done] wrote {DEST / "validation_robustness_stats.csv"}')
print(f'[done] wrote {DEST / "150pairs_with_cos_mini.csv"}')
