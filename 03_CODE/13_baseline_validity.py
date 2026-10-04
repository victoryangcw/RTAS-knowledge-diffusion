# -*- coding: utf-8 -*-
"""13_baseline_validity.py — v1.0-cand.10 (SECONDARY robustness)

Simple similarity baselines on the 150-pair reference set, compared with the
frozen MiniLM embedding cosine. Goal: incremental-validity evidence — does the
semantic embedding carry signal beyond lexical overlap?

Baselines (all on title text only; char n-grams so Chinese+English are handled
symmetrically without a tokenizer):
  B1 TF-IDF cosine          (sklearn TfidfVectorizer, char_wb 3-5 grams)
  B2 Jaccard                (char 3-gram set overlap)
  B3 BM25 Okapi             (rank_bm25 on char 3-grams; rank_bm25 is REQUIRED —
                             the hand-rolled fallback was removed post-audit to
                             eliminate implementation dependence)

POST-AUDIT FIX (2026-10-04): AUC is now tie-aware (roc_auc_score / Mann-Whitney
average ranks). The previous np.argsort unique-rank AUC made scores with heavy
ties (Jaccard/BM25 zero-mass) dependent on sort order.

For each baseline, report:
  - Spearman rho vs human score (1-4)        [compare with frozen MiniLM +0.405]
  - AUC for rating >=2 vs =1                 [compare with MiniLM 0.880]
  - point-biserial r

Frozen inputs read-only. Outputs new files only.
"""
import warnings; warnings.filterwarnings('ignore')
import re, math
from collections import Counter
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except Exception as exc:
    raise ImportError(
        'rank_bm25 is REQUIRED for the frozen BM25 baseline; install it to '
        'avoid implementation-dependent fallback formulas.'
    ) from exc

from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

SEED = 42
BASE = r'D:/dachuang_outputs/SCI_最终投稿图表包'
PROJ = r'D:/vc-task/RTAS_FINAL_PROJECT'
ANN = pd.read_csv(BASE + '/mytask/标注任务_150对_人工LLM混合_已标注.csv')
COS = pd.read_csv(PROJ + '/02_RTAS_MODEL_SELECTION/human_validation/robustness/150pairs_with_cos_mini.csv')
OUT = PROJ + '/02_RTAS_MODEL_SELECTION/human_validation/robustness'

df = ANN[['pair_id', 'project_title', 'paper_title', 'annotator1_score']].merge(
    COS[['pair_id', 'cos_mini']], on='pair_id')
df = df.sort_values('pair_id').reset_index(drop=True)
n = len(df)
y = df['annotator1_score'].astype(int).values
pos = y >= 2


def char_ngrams(s, n=3):
    s = re.sub(r'\s+', ' ', str(s).lower().strip())
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i+n] for i in range(len(s) - n + 1)}


def jaccard(a, b):
    A, B = char_ngrams(a), char_ngrams(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


# ---- B1 TF-IDF cosine (char_wb 3-5 grams) ----
vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)
all_docs = list(df['project_title']) + list(df['paper_title'])
X = vec.fit_transform(all_docs)
Xp, Xa = X[:n], X[n:]
b1 = np.array([cosine_similarity(Xp[i], Xa[i])[0, 0] for i in range(n)])

# ---- B2 Jaccard ----
b2 = np.array([jaccard(df['project_title'].iloc[i], df['paper_title'].iloc[i]) for i in range(n)])

# ---- B3 BM25 (fixed implementation: rank_bm25 BM25Okapi on char 3-grams) ----
def bm25_scores():
    docs = [list(char_ngrams(t)) for t in df['paper_title']]
    bm = BM25Okapi(docs)
    out = np.zeros(n)
    for i in range(n):
        q = list(char_ngrams(df['project_title'].iloc[i]))
        out[i] = bm.get_scores(q)[i]
    return out

b3 = bm25_scores()


def metrics(name, x):
    rho, p = spearmanr(x, y)
    # Tie-aware AUC (Mann-Whitney U with average ranks) == roc_auc_score
    auc = float(roc_auc_score(pos.astype(int), x))
    r_pb = float(np.corrcoef(x, pos.astype(float))[0, 1])
    return {'baseline': name, 'spearman_rho': rho, 'spearman_p': p,
            'auc_ge2_vs_1': auc, 'pointbiserial_r': r_pb, 'n': n}

rows = [
    metrics('MiniLM cosine (frozen)', df['cos_mini'].values),
    metrics('TF-IDF cosine (char 3-5g)', b1),
    metrics('Jaccard (char 3-gram)', b2),
    metrics('BM25 Okapi (char 3-gram)', b3),
]
res = pd.DataFrame(rows)
res.to_csv(OUT + '/baseline_validity.csv', index=False, encoding='utf-8-sig')

# sanity: frozen MiniLM rho must equal +0.405
mini_rho = res.loc[res.baseline.str.startswith('MiniLM'), 'spearman_rho'].iloc[0]
print(f'[sanity] MiniLM rho = {mini_rho:+.4f} (must match frozen +0.405)')
print()
print(res.to_string(index=False))
print()
print(f'[done] wrote {OUT}/baseline_validity.csv')
