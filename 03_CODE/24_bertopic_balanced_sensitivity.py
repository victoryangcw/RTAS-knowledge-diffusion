# -*- coding: utf-8 -*-
"""24_bertopic_balanced_sensitivity.py — v1.1-postaudit (SECONDARY robustness)

Add-on robustness responding to the paper/project imbalance concern: the joint
BERTopic corpus is 56,901 papers vs 3,714 projects (~15:1), so HDBSCAN topic
structure is overwhelmingly shaped by the paper side. This script re-runs the
FROZEN UMAP+HDBSCAN protocol on a 1:1 balanced corpus (all 3,714 projects +
3,714 randomly sampled papers, seed 42) and asks whether the quadrant
asymmetry (HRLT 173 >> LRHT 10) survives.

Design guardrails (printed in output):
  - Quadrant assignment in a balanced corpus uses the SAME rules as frozen
    (paper prevalence top-20% threshold, project prevalence fixed >= 0.5%),
    applied to the balanced-corpus prevalences. This is a COMPOSITION
    sensitivity, not a re-run of the frozen threshold values.
  - BERTopic's class-based c-TF-IDF representation is not re-used; only the
    document->topic assignment matters here (quadrant assignment is
    prevalence-based, per _02_fit_bertopic.py).
  - A single seed-42 paper subsample is used; the point is "does the
    asymmetry survive 1:1 composition", not a full bootstrap over subsamples.

Outputs (private working dir; aggregate counts only):
  03_FINAL_ANALYSIS/topic_model/bertopic_balanced_sensitivity.csv
  03_FINAL_ANALYSIS/topic_model/bertopic_balanced_sensitivity.json
"""
import json
import time
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np
import pandas as pd
from umap import UMAP
from hdbscan import HDBSCAN

ROOT = Path(r'D:/vc-task/RTAS_FINAL_PROJECT')
TM = ROOT / '03_FINAL_ANALYSIS' / 'topic_model'
emb = np.load(TM / 'corpus_embeddings_joint.npy')          # (60615, 384)
projs = pd.read_csv(ROOT / '01_DATA' / 'final_analysis' / 'table5_project_dataset_n3714_full.csv')
papers = pd.read_csv(ROOT / '01_DATA' / 'raw_private' / 'whu_openalex_papers_2020_2024_full.csv')
n_proj, n_paper = len(projs), len(papers)
assert emb.shape[0] == n_proj + n_paper, f'emb rows {emb.shape[0]} != {n_proj + n_paper}'
print(f'[load] emb={emb.shape}; proj={n_proj} paper={n_paper}')

# frozen protocol params (from fit_audit.json)
UMAP_P = dict(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
HDB_P = dict(min_cluster_size=10, min_samples=5, metric='euclidean', cluster_selection_method='eom')

# ---- balanced corpus: all projects + seed-42 paper subsample ----
rng = np.random.default_rng(42)
paper_idx = np.sort(rng.choice(n_paper, size=n_proj, replace=False))
sel = np.concatenate([np.arange(n_proj), n_proj + paper_idx])
emb_b = emb[sel]
src_b = np.array(['project'] * n_proj + ['paper'] * n_proj)
print(f'[balanced] corpus={len(emb_b)} (proj {n_proj} + paper {n_proj}, seed 42)')

t0 = time.time()
um = UMAP(**UMAP_P)
eb = um.fit_transform(emb_b)
hdb = HDBSCAN(**HDB_P)
top = hdb.fit_predict(eb)
out_rate = float(np.mean(top == -1))
uniq = sorted(set(top) - {-1})
print(f'[balanced] topics={len(uniq)} outlier={out_rate:.4f} ({time.time()-t0:.1f}s)')

# quadrant assignment on the balanced corpus (same rules as frozen)
is_p = src_b == 'project'
is_r = src_b == 'paper'
prev_p = np.array([np.sum((top == t) & is_r) / n_proj for t in uniq])  # paper side denom = 3714
prev_j = np.array([np.sum((top == t) & is_p) / n_proj for t in uniq])
# frozen rules: paper prevalence top-20% threshold (with n>=177 fallback on 886 -> here
# 20% of topic count), project prevalence fixed >= 0.5%
thr_p = np.quantile(prev_p, 0.80)
thr_j = 0.005
hp, hj = prev_p >= thr_p, prev_j >= thr_j
counts = dict(HRHT=int(np.sum(hp & hj)), HRLT=int(np.sum(hp & ~hj)),
              LRHT=int(np.sum(~hp & hj)), LRLT=int(np.sum(~hp & ~hj)))
print(f'[balanced] quadrants HRHT/HRLT/LRHT/LRLT = {counts["HRHT"]}/{counts["HRLT"]}/{counts["LRHT"]}/{counts["LRLT"]}')

frozen = dict(HRHT=5, HRLT=173, LRHT=10, LRLT=698, n_topics=886,
              outlier_pct=38.469, n_docs=60615)
out = {
    'date': '2026-10-05',
    'purpose': 'does the HRLT>>LRHT asymmetry survive a 1:1 paper/project corpus?',
    'frozen_reference': frozen,
    'balanced_seed42': dict(n_docs=int(len(emb_b)), n_topics=int(len(uniq)),
                            outlier_pct=round(100 * out_rate, 3),
                            thresholds={'paper': 'top-20% prevalence', 'project': 'fixed >=0.5%'},
                            quadrants=counts),
    'asymmetry_survives': counts['HRLT'] > counts['LRHT'],
}
with open(TM / 'bertopic_balanced_sensitivity.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
row = dict(corpus='balanced_1to1_seed42', n_docs=len(emb_b), n_topics=len(uniq),
           outlier_pct=round(100 * out_rate, 3), **counts)
pd.DataFrame([dict(corpus='frozen_joint_15to1', n_docs=60615, n_topics=886,
                   outlier_pct=38.469, HRHT=5, HRLT=173, LRHT=10, LRLT=698),
              row]).to_csv(TM / 'bertopic_balanced_sensitivity.csv', index=False, encoding='utf-8-sig')
print(f'[done] wrote bertopic_balanced_sensitivity.csv / .json')
print(f'[result] HRLT>LRHT under 1:1 composition: {counts["HRLT"] > counts["LRHT"]} '
      f'({counts["HRLT"]} vs {counts["LRHT"]})')
