# -*- coding: utf-8 -*-
"""17_leave_advisor_out_rtas.py — v1.0-cand.13 (SECONDARY sensitivity, CRITICAL)

Leave-advisor-out (LOO) RTAS sensitivity:
  For each project p in college c, year t, with focal advisor set A_p:
    P^(-A_p)_{c,t} = P_{c,t} \\ { articles authored by any advisor in A_p }
    RTAS_LOO(p) = mean cos(e_p, e_j) for j in P^(-A_p)_{c,t}
  i.e. remove the focal advisor(s)' own publications from the college
  reference portfolio before scoring that project.

PURPOSE: Test whether the HLM advisor-publication coefficient (+0.00427)
is partly mechanical (advisor's own papers enter the reference portfolio
against which their project is scored).

CONSTRAINTS (frozen, per user spec):
  - Same MiniLM embeddings (frozen)
  - Same cumulative window [2020, t]
  - Same mean aggregation (primary RTAS variant)
  - Same MixedLM v2b spec: rtas ~ is_provincial + is_national + year_centered
        + log1p(advisor_prior_3y_works_mean)
        + log1p(advisor_prior_supervised_projects) + (1|college)
  - Match 3231 complete cases from primary model for 1:1 comparison
  - If portfolio becomes empty after removal, report count separately;
    do NOT silently switch denominator

PROVENANCE:
  paper_college_year_map.csv + raw papers (authors) + table5_project_dataset_n3714_full.csv
  + proj_emb_mini.npy + paper_emb_mini.npy
    --(this script)-->
  03_FINAL_ANALYSIS/hlm/rtas_loo/rtas_loo_per_project.csv
  03_FINAL_ANALYSIS/hlm/rtas_loo/hlm_loo_vs_primary_comparison.csv
  03_FINAL_ANALYSIS/hlm/rtas_loo/hlm_loo_summary.txt
"""
import warnings; warnings.filterwarnings('ignore')
import re, os, json, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
import statsmodels.formula.api as smf

BASE = Path(r'D:/dachuang_outputs/SCI_最终投稿图表包/mytask/rtas_freeze')
PROJ = Path(r'D:/vc-task/RTAS_FINAL_PROJECT')
RAW = PROJ / '01_DATA' / 'raw_private'
OUT = PROJ / '03_FINAL_ANALYSIS' / 'hlm' / 'rtas_loo'
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. Load all inputs
# ============================================================
print('='*60)
print('[1] Loading inputs...')
t5 = pd.read_csv(PROJ / '01_DATA' / 'final_analysis' / 'table5_project_dataset_n3714_full.csv')
print(f'  table5: {len(t5)} projects')

MAP = pd.read_csv(BASE / 'paper_college_year_map.csv')
print(f'  paper map: {len(MAP)} papers')

# Join authors from raw papers
raw20 = pd.read_csv(RAW / 'whu_openalex_papers_2020_2024_full.csv',
                    usecols=['work_id', 'authors', 'year'])
f1719 = RAW / 'whu_openalex_papers_2017_2019.csv'
if f1719.exists():
    raw17 = pd.read_csv(f1719, usecols=['work_id', 'authors', 'year'])
    allp = pd.concat([raw20, raw17], ignore_index=True).drop_duplicates(subset=['work_id'])
else:
    allp = raw20
print(f'  raw papers (with authors): {len(allp)}')

MAP = MAP.merge(allp[['work_id', 'authors']], on='work_id', how='left')
print(f'  merged map: {len(MAP)} (authors non-null: {MAP["authors"].notna().sum()})')

emb_paper = np.load(BASE / 'paper_emb_mini.npy')   # (12000, 384)
emb_proj = np.load(BASE / 'proj_emb_mini.npy')     # (3714, 384)
print(f'  paper_emb: {emb_paper.shape}, proj_emb: {emb_proj.shape}')
assert len(emb_paper) == len(MAP)
assert len(emb_proj) == len(t5)

# ============================================================
# 2. Build advisor pinyin index (same as _advisor_covariate_audit.py)
# ============================================================
print('\n' + '='*60)
print('[2] Building advisor pinyin index...')

try:
    from pypinyin import lazy_pinyin, Style
except ImportError:
    raise ImportError('pypinyin required: pip install pypinyin')

def split_advisors(s):
    if not isinstance(s, str): return []
    parts = re.split(r'[、，,;；]', s)
    return [p.strip() for p in parts if p.strip()]

def pinyin_keys(name):
    if not isinstance(name, str) or not name.strip(): return set()
    if re.fullmatch(r'[A-Za-z\- ]+', name):
        k = re.sub(r'[^a-z]', '', name.lower())
        return {k, k[::-1]} if k else set()
    py = lazy_pinyin(name, style=Style.NORMAL)
    if not py or any(p == '' for p in py): return set()
    surname = py[0]
    given = ''.join(py[1:])
    keys = {surname + given, given + surname}
    if len(py) >= 2:
        keys.add(surname + py[1])
    return {k for k in keys if len(k) >= 3}

def norm_author(s):
    if not isinstance(s, str): return ''
    return re.sub(r'[^a-z]', '', s.lower())

# Build advisor atom -> set of pinyin keys
adv_keys = {}
for adv in t5['advisor'].dropna().unique():
    for a in split_advisors(adv):
        ks = pinyin_keys(a)
        if ks: adv_keys[a] = ks

# key -> set of advisor atoms
key_to_advs = defaultdict(set)
for a, ks in adv_keys.items():
    for k in ks:
        key_to_advs[k].add(a)

print(f'  advisor atoms: {len(adv_keys)}, pinyin keys: {len(key_to_advs)}')

# ============================================================
# 3. For each paper, find which advisor atoms authored it
# ============================================================
print('\n' + '='*60)
print('[3] Matching papers to advisor atoms...')
t0 = time.time()

paper_advisors = [set() for _ in range(len(MAP))]  # paper_idx -> set of advisor atoms
ambiguous_atoms = set()

for i, row in MAP.iterrows():
    auths = row.get('authors', '')
    if not isinstance(auths, str) or not auths.strip():
        continue
    for a in auths.split(' | '):
        na = norm_author(a.strip())
        if len(na) < 3: continue
        matched = key_to_advs.get(na, set())
        if len(matched) == 1:
            paper_advisors[i].update(matched)
        elif len(matched) > 1:
            for adv in matched:
                ambiguous_atoms.add(adv)

print(f'  done in {time.time()-t0:.1f}s')
print(f'  ambiguous atoms (excluded): {len(ambiguous_atoms)}')
n_with_adv = sum(1 for s in paper_advisors if s)
print(f'  papers with >=1 matched advisor: {n_with_adv}/{len(MAP)}')

# ============================================================
# 4. Build college -> paper indices (matched only), same as 03_rtas_variants.py
# ============================================================
print('\n' + '='*60)
print('[4] Building college paper portfolios...')
paper_colleges = MAP['colleges'].fillna('').apply(
    lambda s: [c for c in str(s).split(' | ') if c])
paper_years = pd.to_numeric(MAP['year'], errors='coerce').fillna(0).astype(int).values
has_match = MAP['has_matched'].fillna(False).astype(bool).values

college_papers = defaultdict(list)
for i in range(len(MAP)):
    if not has_match[i]:
        continue
    for c in paper_colleges.iloc[i]:
        college_papers[c].append(i)
college_papers = {c: np.array(v) for c, v in college_papers.items()}
print(f'  colleges with papers: {len(college_papers)}')

# ============================================================
# 5. Compute RTAS_LOO for each project
# ============================================================
print('\n' + '='*60)
print('[5] Computing RTAS_LOO (leave-advisor-out) for 3714 projects...')
t0 = time.time()

# Normalize embeddings for cosine
emb_proj_n = emb_proj / np.linalg.norm(emb_proj, axis=1, keepdims=True).clip(min=1e-12)
emb_paper_n = emb_paper / np.linalg.norm(emb_paper, axis=1, keepdims=True).clip(min=1e-12)

records = []
n_empty_orig = 0
n_empty_loo = 0
n_reduced = 0

for i in range(len(t5)):
    c = t5.iloc[i]['college']
    t = int(t5.iloc[i]['year']) if pd.notna(t5.iloc[i]['year']) else 2024

    # Get college's matched paper indices
    pidx = college_papers.get(c, np.array([], dtype=int))
    if len(pidx):
        mask = (paper_years[pidx] >= 2020) & (paper_years[pidx] <= t)
        pidx = pidx[mask]

    n_orig = len(pidx)
    if n_orig == 0:
        n_empty_orig += 1
        records.append({
            'proj_idx': i, 'project_id': t5.iloc[i].get('project_id', ''),
            'college': c, 'year': t,
            'n_papers_orig': 0, 'n_papers_loo': 0, 'n_removed': 0,
            'pct_removed': np.nan,
            'rtas_orig': np.nan, 'rtas_loo': np.nan,
            'rtas_diff': np.nan,
        })
        continue

    # Focal advisors for this project
    adv_field = t5.iloc[i].get('advisor', '')
    focal_advisors = set(split_advisors(adv_field))
    # Exclude ambiguous atoms
    focal_advisors = {a for a in focal_advisors if a in adv_keys and a not in ambiguous_atoms}

    # Find papers authored by any focal advisor
    if focal_advisors:
        keep_mask = np.array([
            not (paper_advisors[pi] & focal_advisors)
            for pi in pidx
        ])
        pidx_loo = pidx[keep_mask]
    else:
        pidx_loo = pidx

    n_loo = len(pidx_loo)
    n_removed = n_orig - n_loo

    if n_removed > 0:
        n_reduced += 1
    if n_loo == 0:
        n_empty_loo += 1

    # Compute RTAS_orig and RTAS_LOO (mean aggregation, same as primary)
    pe = emb_proj_n[i]
    rtas_orig = float((emb_paper_n[pidx] @ pe).mean())
    rtas_loo = float((emb_paper_n[pidx_loo] @ pe).mean()) if n_loo > 0 else np.nan

    records.append({
        'proj_idx': i,
        'project_id': t5.iloc[i].get('project_id', ''),
        'college': c, 'year': t,
        'n_papers_orig': n_orig, 'n_papers_loo': n_loo,
        'n_removed': n_removed,
        'pct_removed': (n_removed / n_orig * 100) if n_orig > 0 else np.nan,
        'rtas_orig': rtas_orig,
        'rtas_loo': rtas_loo,
        'rtas_diff': rtas_loo - rtas_orig if not np.isnan(rtas_loo) else np.nan,
    })

    if (i + 1) % 1000 == 0:
        print(f'  {i+1}/3714 done ({time.time()-t0:.1f}s)')

LOO = pd.DataFrame(records)
print(f'  done in {time.time()-t0:.1f}s')
print(f'  projects with empty original portfolio: {n_empty_orig}')
print(f'  projects with empty LOO portfolio: {n_empty_loo}')
print(f'  projects with >=1 paper removed: {n_reduced}')

# ============================================================
# 6. Save per-project LOO RTAS
# ============================================================
LOO_PATH = OUT / 'rtas_loo_per_project.csv'
LOO.to_csv(LOO_PATH, index=False, encoding='utf-8-sig')
print(f'\n  saved {LOO_PATH}')

# ============================================================
# 7. Summary stats: correlation, mean/SD difference
# ============================================================
print('\n' + '='*60)
print('[7] RTAS_orig vs RTAS_LOO comparison:')
v = LOO.dropna(subset=['rtas_orig', 'rtas_loo'])
print(f'  valid pairs: {len(v)}')
r_p, p_p = pearsonr(v['rtas_orig'], v['rtas_loo'])
r_s, p_s = spearmanr(v['rtas_orig'], v['rtas_loo'])
print(f'  Pearson r={r_p:.4f} (p={p_p:.3g})')
print(f'  Spearman rho={r_s:.4f} (p={p_s:.3g})')
print(f'  RTAS_orig: mean={v["rtas_orig"].mean():.4f} SD={v["rtas_orig"].std():.4f}')
print(f'  RTAS_LOO:  mean={v["rtas_loo"].mean():.4f} SD={v["rtas_loo"].std():.4f}')
print(f'  diff (LOO-orig): mean={v["rtas_diff"].mean():+.6f} SD={v["rtas_diff"].std():.6f}')

print(f'\n  portfolio reduction stats (projects with >=1 removed):')
red = LOO[LOO['n_removed'] > 0]
print(f'  n projects: {len(red)}')
print(f'  n_removed: mean={red["n_removed"].mean():.2f} max={red["n_removed"].max()}')
print(f'  pct_removed: mean={red["pct_removed"].mean():.2f}% max={red["pct_removed"].max():.2f}%')

# ============================================================
# 8. Build LOO model frame (same as primary HLM)
# ============================================================
print('\n' + '='*60)
print('[8] Building HLM model frame with RTAS_LOO...')
df = t5.copy()
df['is_provincial'] = df['level'].astype(str).str.contains('省级|Provincial', regex=True).astype(int)
df['is_national'] = df['level'].astype(str).str.contains('国家级|National', regex=True).astype(int)
df['year_centered'] = df['year'] - 2022
df['log_prior3y'] = np.log1p(pd.to_numeric(df['advisor_prior_3y_works_mean'], errors='coerce'))
# v2b spec: use advisor_prior_supervised_projects (future-leak-free), NOT total
df['log_prior_supervision'] = np.log1p(df['advisor_prior_supervised_projects'])

# Attach RTAS_LOO
df['rtas_loo'] = LOO['rtas_loo'].values

formula = ('rtas ~ is_provincial + is_national + year_centered '
           '+ log_prior3y + log_prior_supervision')
formula_loo = ('rtas_loo ~ is_provincial + is_national + year_centered '
               '+ log_prior3y + log_prior_supervision')


def fit_and_compare(sub, formula, dep_var, label):
    sub = sub.dropna(subset=[dep_var, 'log_prior3y', 'log_prior_supervision',
                             'is_provincial', 'is_national', 'year_centered', 'college'])
    print(f'\n--- {label}: n={len(sub)}, colleges={sub["college"].nunique()} ---')
    md = smf.mixedlm(formula, sub, groups=sub['college'])
    res = md.fit(reml=True, method='lbfgs', maxiter=2000)

    var_g = float(res.cov_re.iloc[0, 0]) if res.cov_re.size else 0.0
    var_e = res.scale
    icc = var_g / (var_g + var_e)

    # Marginal R2 (fixed only) and conditional R2 (fixed + random)
    # Nakagawa & Schielzeth 2013
    fixef = res.fe_params
    X = md.exog  # design matrix for fixed effects
    y = sub[dep_var].values
    y_pred_fix = X @ fixef
    ss_res = float(np.sum((y - y_pred_fix - sub.groupby('college')[dep_var].transform('mean').values + y.mean())**2))
    # Simpler: var_fixed = var(fixed predictions)
    var_fixed = float(np.var(y_pred_fix))
    var_total = float(np.var(y))
    r2_marginal = var_fixed / (var_fixed + var_g + var_e)
    r2_conditional = (var_fixed + var_g) / (var_fixed + var_g + var_e)

    print(f'  var_college={var_g:.6f} var_resid={var_e:.6f} ICC={icc:.4f}')
    print(f'  marginal R2={r2_marginal:.4f}  conditional R2={r2_conditional:.4f}')

    co = pd.DataFrame({
        'term': res.params.index,
        'coef': res.params.values,
        'se': res.bse.values,
        'z': res.tvalues.values,
        'p': res.pvalues.values,
        'ci_low': res.conf_int()[0].values,
        'ci_high': res.conf_int()[1].values,
    })
    co['stars'] = np.where(co['p'] < 0.001, '***',
                  np.where(co['p'] < 0.01, '**',
                  np.where(co['p'] < 0.05, '*', 'ns')))
    print(co.round(6).to_string(index=False))
    return res, co, icc, r2_marginal, r2_conditional, len(sub)


# Primary model (RTAS_orig) for baseline reference
res_p, co_p, icc_p, r2m_p, r2c_p, n_p = fit_and_compare(
    df, formula, 'rtas', 'PRIMARY (RTAS_orig)')

# LOO model
res_l, co_l, icc_l, r2m_l, r2c_l, n_l = fit_and_compare(
    df, formula_loo, 'rtas_loo', 'LOO (RTAS_leave_advisor_out)')

# ============================================================
# 9. Side-by-side coefficient comparison
# ============================================================
print('\n' + '='*60)
print('[9] Coefficient comparison: PRIMARY vs LOO')
cmp = co_p[['term', 'coef', 'se', 'p', 'ci_low', 'ci_high', 'stars']].merge(
    co_l[['term', 'coef', 'se', 'p', 'ci_low', 'ci_high', 'stars']],
    on='term', suffixes=('_primary', '_loo'), how='outer')
cmp['delta_coef'] = cmp['coef_loo'] - cmp['coef_primary']
print(cmp.round(6).to_string(index=False))

CMP_PATH = OUT / 'hlm_loo_vs_primary_comparison.csv'
cmp.to_csv(CMP_PATH, index=False, encoding='utf-8-sig')
print(f'\n  saved {CMP_PATH}')

# ============================================================
# 10. Summary file
# ============================================================
summary = {
    'rtas_orig': {
        'mean': float(v['rtas_orig'].mean()),
        'sd': float(v['rtas_orig'].std()),
    },
    'rtas_loo': {
        'mean': float(v['rtas_loo'].mean()),
        'sd': float(v['rtas_loo'].std()),
    },
    'correlation': {
        'pearson_r': float(r_p), 'pearson_p': float(p_p),
        'spearman_r': float(r_s), 'spearman_p': float(p_s),
    },
    'rtas_diff': {
        'mean': float(v['rtas_diff'].mean()),
        'sd': float(v['rtas_diff'].std()),
    },
    'portfolio_reduction': {
        'n_projects_with_removal': int(n_reduced),
        'n_projects_empty_loo': int(n_empty_loo),
        'mean_n_removed': float(red['n_removed'].mean()) if len(red) else 0,
        'max_n_removed': int(red['n_removed'].max()) if len(red) else 0,
        'mean_pct_removed': float(red['pct_removed'].mean()) if len(red) else 0,
    },
    'hlm_primary': {
        'n': n_p, 'icc': float(icc_p),
        'marginal_r2': float(r2m_p), 'conditional_r2': float(r2c_p),
        'log_prior3y_coef': float(co_p.loc[co_p.term == 'log_prior3y', 'coef'].iloc[0]),
        'log_prior3y_ci': [float(co_p.loc[co_p.term == 'log_prior3y', 'ci_low'].iloc[0]),
                           float(co_p.loc[co_p.term == 'log_prior3y', 'ci_high'].iloc[0])],
        'log_prior3y_p': float(co_p.loc[co_p.term == 'log_prior3y', 'p'].iloc[0]),
    },
    'hlm_loo': {
        'n': n_l, 'icc': float(icc_l),
        'marginal_r2': float(r2m_l), 'conditional_r2': float(r2c_l),
        'log_prior3y_coef': float(co_l.loc[co_l.term == 'log_prior3y', 'coef'].iloc[0]),
        'log_prior3y_ci': [float(co_l.loc[co_l.term == 'log_prior3y', 'ci_low'].iloc[0]),
                           float(co_l.loc[co_l.term == 'log_prior3y', 'ci_high'].iloc[0])],
        'log_prior3y_p': float(co_l.loc[co_l.term == 'log_prior3y', 'p'].iloc[0]),
    },
    'delta_log_prior3y_coef': float(
        co_l.loc[co_l.term == 'log_prior3y', 'coef'].iloc[0] -
        co_p.loc[co_p.term == 'log_prior3y', 'coef'].iloc[0]),
}
SUM_PATH = OUT / 'hlm_loo_summary.json'
with open(SUM_PATH, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f'\n  saved {SUM_PATH}')

# Text summary
TXT_PATH = OUT / 'hlm_loo_summary.txt'
with open(TXT_PATH, 'w', encoding='utf-8') as f:
    f.write('Leave-Advisor-Out RTAS Sensitivity Analysis\n')
    f.write('='*60 + '\n\n')
    f.write(f'Valid pairs: {len(v)}\n')
    f.write(f'RTAS_orig: mean={v["rtas_orig"].mean():.4f} SD={v["rtas_orig"].std():.4f}\n')
    f.write(f'RTAS_LOO:  mean={v["rtas_loo"].mean():.4f} SD={v["rtas_loo"].std():.4f}\n')
    f.write(f'Pearson r={r_p:.4f}, Spearman rho={r_s:.4f}\n')
    f.write(f'diff (LOO-orig): mean={v["rtas_diff"].mean():+.6f} SD={v["rtas_diff"].std():.6f}\n\n')
    f.write(f'Portfolio reduction:\n')
    f.write(f'  projects with >=1 paper removed: {n_reduced}\n')
    f.write(f'  projects with empty LOO portfolio: {n_empty_loo}\n')
    f.write(f'  mean n_removed: {red["n_removed"].mean():.2f}\n' if len(red) else '  no reductions\n')
    f.write(f'  mean pct_removed: {red["pct_removed"].mean():.2f}%\n\n' if len(red) else '')
    f.write('\n--- HLM Primary (RTAS_orig) ---\n')
    f.write(str(res_p.summary()))
    f.write(f'\nn={n_p}, ICC={icc_p:.4f}, marginal R2={r2m_p:.4f}, conditional R2={r2c_p:.4f}\n\n')
    f.write('\n--- HLM LOO (RTAS_leave_advisor_out) ---\n')
    f.write(str(res_l.summary()))
    f.write(f'\nn={n_l}, ICC={icc_l:.4f}, marginal R2={r2m_l:.4f}, conditional R2={r2c_l:.4f}\n\n')
    f.write('\n--- Coefficient Comparison ---\n')
    f.write(cmp.round(6).to_string(index=False))
print(f'  saved {TXT_PATH}')

print('\n' + '='*60)
print('[DONE] Leave-advisor-out sensitivity complete.')
print(f'  log_prior3y: primary={co_p.loc[co_p.term=="log_prior3y","coef"].iloc[0]:+.6f}'
      f'  LOO={co_l.loc[co_l.term=="log_prior3y","coef"].iloc[0]:+.6f}'
      f'  delta={summary["delta_log_prior3y_coef"]:+.6f}')
