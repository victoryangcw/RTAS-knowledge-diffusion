# -*- coding: utf-8 -*-
"""14_bertopic_sensitivity.py — v1.0-cand.10 (SECONDARY robustness)

Clustering-parameter sensitivity for the BERTopic topic model. Uses the cached
joint MiniLM embeddings (corpus_embeddings_joint.npy) and re-runs
UMAP + HDBSCAN under alternative hyperparameter sets. Reports:
  - outlier rate (fraction docs -> topic -1)
  - non-outlier topic count
  - Spearman corr(topic paper-prevalence rank, topic project-prevalence rank)
    [aggregate quadrant-direction stability: do high-paper topics stay
     high-project across param sets?]
  - quadrant count distribution (HRHT/HRLT/LRHT/LRLT) under top-20% threshold

Does NOT modify any frozen output. New file only.
Default-param run is a sanity check (should reproduce ~886 topics / ~38.47% outlier).
"""
import warnings; warnings.filterwarnings('ignore')
import time
import numpy as np
import pandas as pd
from umap import UMAP
from hdbscan import HDBSCAN

ROOT = r'D:/vc-task/RTAS_FINAL_PROJECT'
EMB_CACHE = ROOT + '/03_FINAL_ANALYSIS/topic_model/corpus_embeddings_joint.npy'
PROJ_CSV = ROOT + '/01_DATA/final_analysis/table5_project_dataset_n3714_full.csv'
PAPER_CSV = ROOT + '/01_DATA/raw_private/whu_openalex_papers_2020_2024_full.csv'
OUT = ROOT + '/03_FINAL_ANALYSIS/topic_model'

emb = np.load(EMB_CACHE)
projs = pd.read_csv(PROJ_CSV)
papers = pd.read_csv(PAPER_CSV)
n_proj, n_paper = len(projs), len(papers)
doc_source = np.array(['project'] * n_proj + ['paper'] * n_paper)
print(f'[load] emb={emb.shape}, proj={n_proj}, paper={n_paper}')

SETS = {
    'default':   dict(n_neighbors=15, n_components=5, min_dist=0.0, min_cluster_size=10, min_samples=5),
    'mc15_ms7':  dict(n_neighbors=15, n_components=5, min_dist=0.0, min_cluster_size=15, min_samples=7),
    'mc20_ms10': dict(n_neighbors=15, n_components=5, min_dist=0.0, min_cluster_size=20, min_samples=10),
    'mc8_ms3':   dict(n_neighbors=15, n_components=5, min_dist=0.0, min_cluster_size=8,  min_samples=3),
}


def quadrant_counts(topics, doc_source, n_proj, n_paper, q=0.80):
    """Return dict of HRHT/HRLT/LRHT/LRLT counts + Spearman(prev_paper, prev_project)."""
    is_proj = doc_source == 'project'
    is_paper = doc_source == 'paper'
    uniq = sorted(set(topics) - {-1})
    if not uniq:
        return dict(HRHT=0, HRLT=0, LRHT=0, LRLT=0, n_topics=0, spearman=np.nan)
    prev_paper = np.array([np.sum((topics == t) & is_paper) / n_paper for t in uniq])
    prev_proj = np.array([np.sum((topics == t) & is_proj) / n_proj for t in uniq])
    thr_p = np.quantile(prev_paper, q)
    thr_j = np.quantile(prev_proj, q)
    hp, hj = prev_paper >= thr_p, prev_proj >= thr_j
    counts = dict(
        HRHT=int(np.sum(hp & hj)),
        HRLT=int(np.sum(hp & ~hj)),
        LRHT=int(np.sum(~hp & hj)),
        LRLT=int(np.sum(~hp & ~hj)),
    )
    rho = float(np.corrcoef(np.argsort(np.argsort(prev_paper)),
                            np.argsort(np.argsort(prev_proj)))[0, 1])
    counts['n_topics'] = len(uniq)
    counts['spearman_prev'] = rho
    return counts

rows = []
for name, p in SETS.items():
    t0 = time.time()
    umap_model = UMAP(n_neighbors=p['n_neighbors'], n_components=p['n_components'],
                      min_dist=p['min_dist'], metric='cosine', random_state=42)
    emb_r = umap_model.fit_transform(emb)
    hdb = HDBSCAN(min_cluster_size=p['min_cluster_size'], min_samples=p['min_samples'],
                  metric='euclidean', cluster_selection_method='eom')
    topics = hdb.fit_predict(emb_r)
    outlier_rate = float(np.mean(topics == -1))
    qc = quadrant_counts(topics, doc_source, n_proj, n_paper)
    row = dict(param_set=name, **p, outlier_rate=outlier_rate,
                n_topics=qc['n_topics'], rho_paper_proj=qc['spearman_prev'],
                HRHT=qc['HRHT'], HRLT=qc['HRLT'], LRHT=qc['LRHT'], LRLT=qc['LRLT'],
                time_s=round(time.time() - t0, 1))
    rows.append(row)
    print(f"[{name}] outlier={outlier_rate:.4f} topics={qc['n_topics']} "
          f"rho={qc['spearman_prev']:+.3f} HRHT/HRLT/LRHT/LRLT={qc['HRHT']}/{qc['HRLT']}/{qc['LRHT']}/{qc['LRLT']} ({row['time_s']}s)")

df = pd.DataFrame(rows)
df.to_csv(OUT + '/bertopic_clustering_sensitivity.csv', index=False, encoding='utf-8-sig')
print()
print(df.to_string(index=False))
print()
# sanity
default_outlier = df.loc[df.param_set == 'default', 'outlier_rate'].iloc[0]
print(f'[sanity] default outlier_rate={default_outlier:.4f} (frozen ~0.3847)')
print(f'[done] wrote {OUT}/bertopic_clustering_sensitivity.csv')
