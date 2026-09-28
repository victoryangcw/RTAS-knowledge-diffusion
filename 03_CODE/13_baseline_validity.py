# -*- coding: utf-8 -*-
"""13_baseline_validity.py — v1.0-cand.10 (SECONDARY robustness)

Simple similarity baselines on the 150-pair reference set, compared with the
frozen MiniLM embedding cosine. Goal: incremental-validity evidence — does the
semantic embedding carry signal beyond lexical overlap?

Baselines (all on title text only; char n-grams so Chinese+English are handled
symmetrically without a tokenizer):
  B1 TF-IDF cosine          (sklearn TfidfVectorizer, char_wb 3-5 grams)
  B2 Jaccard                (char 3-gram set overlap)
  B3 BM25 Okapi             (rank_bm25 on char 3-grams if available, else hand-rolled)

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
except Exception:
    HAS_BM25 = False

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

# ---- B3 BM25 ----
def bm25_scores():
    docs = [list(char_ngrams(t)) for t in df['paper_title']]
    if HAS_BM25:
        bm = BM25Okapi(docs)
        return np.array([bm.get_score(list(char_ngrams(df['project_title'].iloc[i])), i) for i in range(n)])
    # hand-rolled Okapi BM25
    N = len(docs)
    k1, b = 1.5, 0.75
    df_ = Counter()
    for d in docs:
        for w in set(d):
            df_[w] += 1
    avgdl = np.mean([len(d) for d in docs]) or 1.0
    idf = {w: math.log(1 + (N - f + 0.5) / (f + 0.5)) for w, f in df_.items()}
    out = np.zeros(n)
    for i in range(n):
        q = Counter(char_ngrams(df['project_title'].iloc[i]))
        d = docs[i]
        dl = len(d) or 1
        tf = Counter(d)
        s = 0.0
        for w, qf in q.items():
            if w not in tf:
                continue
            s += idf.get(w, 0) * (tf[w] * (k1 + 1)) / (tf[w] + k1 * (1 - b + b * dl / avgdl))
        out[i] = s
    return out

b3 = bm25_scores()


def metrics(name, x):
    rho, p = spearmanr(x, y)
    # AUC: pos vs neg (higher x => relevant)
    order = np.argsort(x)
    ranks = np.empty(n); ranks[order] = np.arange(1, n + 1)
    n_pos = int(pos.sum()); n_neg = n - n_pos
    auc = (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg) if n_pos and n_neg else np.nan
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
