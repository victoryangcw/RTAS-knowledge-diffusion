import pandas as pd
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score, cohen_kappa_score

# Load anonymized hard-pair ratings
rpt = pd.read_csv('hard_pair_ratings_anonymized.csv', encoding='utf-8-sig')

print('=== Hard-Pair Validation Summary ===')
print(f'N pairs: {len(rpt)}')

# Inter-rater reliability
a = rpt['rater_a_score'].values
b = rpt['rater_b_score'].values
print(f'\nInter-rater reliability:')
print(f'  Quadratic weighted kappa: {cohen_kappa_score(a, b, weights="quadratic"):.4f}')
print(f'  Linear weighted kappa: {cohen_kappa_score(a, b, weights="linear"):.4f}')
print(f'  Exact agreement: {np.mean(a == b)*100:.1f}%')
print(f'  Within 1 point: {np.mean(np.abs(a - b) <= 1)*100:.1f}%')

# Overall correlation with cosine
rho, p = stats.spearmanr(rpt['cosine_similarity'], rpt['consensus_score'])
print(f'\nOverall correlation (cosine vs consensus):')
print(f'  Spearman rho: {rho:.4f} (p={p:.2e})')

# Overall AUC
binary = (rpt['consensus_score'] >= 2).astype(int)
auc = roc_auc_score(binary, rpt['cosine_similarity'])
print(f'  AUC: {auc:.4f}')
print(f'  Related (>=2): {binary.sum()} ({binary.sum()/len(binary)*100:.1f}%)')
print(f'  Unrelated (=1): {(1-binary).sum()} ({(1-binary).sum()/len(binary)*100:.1f}%)')

# Stratified results
print(f'\n=== Stratified by sampling stratum ===')
for stratum in ['random_cross_unit', 'random_same_unit', 'mid_similarity', 'high_similarity']:
    sub = rpt[rpt['stratum'] == stratum]
    n = len(sub)
    rho, p = stats.spearmanr(sub['cosine_similarity'], sub['consensus_score'])
    binary_sub = (sub['consensus_score'] >= 2).astype(int)
    if binary_sub.sum() > 0 and binary_sub.sum() < len(binary_sub):
        auc_val = roc_auc_score(binary_sub, sub['cosine_similarity'])
        auc_str = f'{auc_val:.4f}'
    else:
        auc_str = 'N/A (single class)'
    print(f'\n{stratum} (n={n}):')
    print(f'  Spearman rho: {rho:.4f} (p={p:.2e})')
    print(f'  AUC: {auc_str}')
    print(f'  Related: {binary_sub.sum()}/{len(binary_sub)} ({binary_sub.sum()/len(binary_sub)*100:.1f}%)')

# High-similarity bootstrap CI
hs = rpt[rpt['stratum'] == 'high_similarity']
binary_hs = (hs['consensus_score'] >= 2).astype(int)
B = 10000
rng = np.random.RandomState(42)
n = len(hs)
aucs = []
for b in range(B):
    idx = rng.choice(n, size=n, replace=True)
    sub = hs.iloc[idx]
    y = (sub['consensus_score'] >= 2).astype(int)
    if y.sum() > 0 and y.sum() < len(y):
        aucs.append(roc_auc_score(y, sub['cosine_similarity']))
aucs = np.array(aucs)
ci_low, ci_high = np.percentile(aucs, [2.5, 97.5])
print(f'\nHigh-similarity stratum bootstrap:')
print(f'  n={len(hs)}; related={binary_hs.sum()}, unrelated={(1-binary_hs).sum()}')
print(f'  AUC: {roc_auc_score(binary_hs, hs["cosine_similarity"]):.4f}')
print(f'  Bootstrap 95% CI: [{ci_low:.3f}, {ci_high:.3f}] (B={B}, seed 42)')
print(f'  Valid bootstrap samples: {len(aucs)}/{B}')
