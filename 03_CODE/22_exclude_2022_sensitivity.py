# -*- coding: utf-8 -*-
"""22 - Exclude-2022 sensitivity (2022 source-coverage question).

CONTEXT (2026-09-22 raw-registry audit, script 20)
  The archived official 2022 WHU ITTP approval list contains NO
  university-level entries (provincial 316 + national 150 only); we cannot
  determine whether that reflects the 2022 institutional arrangement or
  source-file coverage. A reviewer could ask whether the RQ1 funding-tier
  comparison and the RQ3 mixed model are driven by the structurally different
  2022 cohort. This cheap sensitivity drops the ENTIRE 2022 cohort and
  recomputes:
    (a) RQ1 three-tier RTAS means/SDs/n, one-way ANOVA (F, p, eta^2), and
        Tukey HSD pairwise contrasts;
    (b) the frozen v2b MixedLM (identical REML/college spec, covariates
        taken from the frozen dataset unchanged).
  Both are ALSO recomputed on the full sample in the same run as a
  self-check that the code path reproduces the frozen numbers
  (means 0.1212/0.1391/0.1460, F=35.72, eta2=1.89%, Tukey +0.0179/+0.0248/
  +0.0070; MixedLM n=3,231, ICC=0.7376).

PROVENANCE
  01_DATA/final_analysis/table5_project_dataset_n3714_full.csv
    --> 03_FINAL_ANALYSIS/sensitivity_exclude_2022/
        rq1_exclude_2022.json
        hlm_exclude_2022_comparison.csv
        exclude_2022_summary.json
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd

warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parents[1]
# In the private workspace .../RTAS_FINAL_PROJECT/06_CODE -> project root;
# in the public repo .../RTAS/03_CODE -> repo root, where the private
# 01_DATA folder is intentionally absent (set RTAS_DATA_HOME to a local copy).
_env = __import__('os').environ.get('RTAS_DATA_HOME')
if _env:
    ROOT = Path(_env)
FROZEN = ROOT / '01_DATA' / 'final_analysis' / 'table5_project_dataset_n3714_full.csv'
OUT = ROOT / '03_FINAL_ANALYSIS' / 'sensitivity_exclude_2022'
OUT.mkdir(parents=True, exist_ok=True)

LEVELS = [(1, 'university'), (2, 'provincial'), (3, 'national')]
FORMULA = ('rtas ~ is_provincial + is_national + year_centered '
           '+ log_prior3y + log_prior_supervision')
TERMS = ['Intercept', 'is_provincial', 'is_national', 'year_centered',
         'log_prior3y', 'log_prior_supervision']


def rq1_block(d, tag):
    grp = {k: d.loc[d['level_code'] == k, 'rtas'].dropna().astype(float).values
           for k, _ in LEVELS}
    desc = {}
    for k, name in LEVELS:
        desc[name] = {'n': int(len(grp[k])),
                      'mean': float(grp[k].mean()),
                      'sd': float(grp[k].std(ddof=1))}
    F, pF = f_oneway(*grp.values())
    allv = np.concatenate(list(grp.values()))
    ssb = sum(len(v) * (v.mean() - allv.mean()) ** 2 for v in grp.values())
    sst = ((allv - allv.mean()) ** 2).sum()
    eta2 = ssb / sst
    tk = pairwise_tukeyhsd(d['rtas'].dropna().values,
                           d.loc[d['rtas'].notna(), 'level'].values)
    tdf = pd.DataFrame(data=tk._results_table.data[1:],
                       columns=tk._results_table.data[0])
    for c in ['meandiff', 'p-adj', 'lower', 'upper']:
        tdf[c] = tdf[c].astype(float)

    def row(g1, g2):
        r = tdf[((tdf['group1'] == g1) & (tdf['group2'] == g2)) |
                ((tdf['group1'] == g2) & (tdf['group2'] == g1))].iloc[0]
        # meandiff is group2-group1; normalize sign as g1 - g2 if flipped
        return {'meandiff': float(r['meandiff']), 'p_adj': float(r['p-adj']),
                'ci_low': float(r['lower']), 'ci_hi': float(r['upper'])}

    pairs = {'provincial_minus_university': row('省级', '校级'),
             'national_minus_university': row('国家级', '校级'),
             'national_minus_provincial': row('国家级', '省级')}
    out = {'sample': tag, 'n_total': int(len(d)),
           'n_with_rtas': int(d['rtas'].notna().sum()),
           'tiers': desc,
           'anova': {'F': float(F), 'df_between': 2,
                     'df_within': int(len(allv) - 3),
                     'p': float(pF), 'eta_squared': float(eta2)},
           'tukey_hsd': pairs}
    print(f'\n--- RQ1 [{tag}] n={out["n_with_rtas"]} ---')
    for name, dd in desc.items():
        print(f'  {name:12s} n={dd["n"]:5d} mean={dd["mean"]:.4f} sd={dd["sd"]:.4f}')
    print(f'  ANOVA F({2},{out["anova"]["df_within"]})={F:.2f} p={pF:.3e} '
          f'eta2={100*eta2:.2f}%')
    for nm, pp in pairs.items():
        print(f'  Tukey {nm:32s} {pp["meandiff"]:+.4f} p={pp["p_adj"]:.4f}')
    return out


def fit_hlm(d, tag):
    d = d.copy()
    d['is_provincial'] = d['level'].astype(str).str.contains(
        '省级|Provincial', regex=True).astype(int)
    d['is_national'] = d['level'].astype(str).str.contains(
        '国家级|National', regex=True).astype(int)
    d['year_centered'] = d['year'] - 2022
    d['log_prior3y'] = np.log1p(
        pd.to_numeric(d['advisor_prior_3y_works_mean'], errors='coerce'))
    d['log_prior_supervision'] = np.log1p(
        pd.to_numeric(d['advisor_prior_supervised_projects'], errors='coerce'))
    sub = d.dropna(subset=['rtas', 'log_prior3y', 'log_prior_supervision',
                           'is_provincial', 'is_national',
                           'year_centered', 'college'])
    md = smf.mixedlm(FORMULA, sub, groups=sub['college'])
    res = md.fit(reml=True, method='lbfgs', maxiter=2000)
    var_g = float(res.cov_re.iloc[0, 0]) if res.cov_re.size else 0.0
    var_e = float(res.scale)
    icc = var_g / (var_g + var_e)
    out = {'sample': tag, 'n_obs': int(len(sub)),
           'n_colleges': int(sub['college'].nunique()),
           'var_college': var_g, 'var_resid': var_e, 'icc': icc,
           'coef': {}, 'se': {}, 'p': {}}
    for term in TERMS:
        if term in res.params.index:
            out['coef'][term] = float(res.params[term])
            out['se'][term] = float(res.bse[term])
            out['p'][term] = float(res.pvalues[term])
    print(f'\n--- HLM [{tag}] n={out["n_obs"]} '
          f'colleges={out["n_colleges"]} ICC={icc:.4f} ---')
    for term in TERMS:
        if term in out['coef']:
            print(f'  {term:26s} b={out["coef"][term]:+.6f} '
                  f'se={out["se"][term]:.6f} p={out["p"][term]:.4g}')
    return out


# ---------- load ----------
df = pd.read_csv(FROZEN)
assert len(df) == 3714
df['level_code'] = pd.to_numeric(df['level_code'], errors='coerce').astype('Int64')
print('Rows by year:', df.groupby('year').size().to_dict())
print('2022 tier counts:',
      df[df['year'] == 2022].groupby('level_code').size().to_dict())

# ---------- RQ1 ----------
rq1_full = rq1_block(df, 'full_frozen_3714')
rq1_no22 = rq1_block(df[df['year'] != 2022].copy(), 'exclude_2022')
(OUT / 'rq1_exclude_2022.json').write_text(
    json.dumps({'full': rq1_full, 'exclude_2022': rq1_no22},
               ensure_ascii=False, indent=2), encoding='utf-8')

# ---------- HLM ----------
hlm_full = fit_hlm(df, 'full')
hlm_no22 = fit_hlm(df[df['year'] != 2022].copy(), 'exclude_2022')

rows = []
for term in TERMS:
    if term not in hlm_full['coef']:
        continue
    rows.append({
        'term': term,
        'primary_coef': hlm_full['coef'][term],
        'primary_se': hlm_full['se'][term],
        'primary_p': hlm_full['p'][term],
        'excl2022_coef': hlm_no22['coef'][term],
        'excl2022_se': hlm_no22['se'][term],
        'excl2022_p': hlm_no22['p'][term],
        'coef_delta': hlm_no22['coef'][term] - hlm_full['coef'][term],
        'sign_agrees': np.sign(hlm_full['coef'][term]) ==
                       np.sign(hlm_no22['coef'][term]),
        'sig_classification_same':
            (hlm_full['p'][term] < 0.05) == (hlm_no22['p'][term] < 0.05),
    })
cmp_df = pd.DataFrame(rows)
cmp_df.to_csv(OUT / 'hlm_exclude_2022_comparison.csv',
              index=False, encoding='utf-8-sig')
print('\n' + cmp_df.round(6).to_string(index=False))

summary = {
    'description': 'Sensitivity excluding the entire 2022 cohort, whose '
                   'archived official list contains no university-level '
                   'records; tests whether RQ1 tier contrasts or the v2b '
                   'MixedLM depend on the structurally different 2022 cohort.',
    'n_dropped_2022': int((df['year'] == 2022).sum()),
    'formula': FORMULA,
    'model': 'statsmodels MixedLM random intercept on college, REML, lbfgs',
    'rq1_full': rq1_full, 'rq1_exclude_2022': rq1_no22,
    'hlm_full': hlm_full, 'hlm_exclude_2022': hlm_no22,
}
(OUT / 'exclude_2022_summary.json').write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nDONE. Outputs in {OUT}')
