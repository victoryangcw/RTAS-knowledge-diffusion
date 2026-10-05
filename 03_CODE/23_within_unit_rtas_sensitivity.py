# -*- coding: utf-8 -*-
"""23_within_unit_rtas_sensitivity.py — v1.1-postaudit (SECONDARY robustness)

Add-on robustness responding to the within-unit calibration concern: raw RTAS
levels may partly reflect discipline-specific title conventions / portfolio
breadth rather than project-level alignment. This script re-estimates the
frozen models after REPLACING raw RTAS with its WITHIN-unit-year standardized
version (college x year z-score), which removes every unit- and year-level
baseline component by construction and leaves only within-unit-year relative
alignment.

Interpretation guardrail (printed in output): this does NOT remove
discipline-specific titling WITHIN a unit-year (e.g., 化学 vs 文学院项目仍可能
共享学院但学科不同); it removes only the BETWEEN-unit-year baseline. For the
frozen college x year cells (n>=2 in all but one single-project unit) this is
well defined; the single-project unit (School of International Education,
2024) is undefined for within-unit-year z-scoring and is excluded from the
z-scored analysis by design (it also supplies no complete case in the frozen
mixed model).

Outputs (private working dir; aggregated only, no project-level data):
  03_FINAL_ANALYSIS/hlm/within_unit_rtas/within_unit_rtas_sensitivity.csv
  03_FINAL_ANALYSIS/hlm/within_unit_rtas/within_unit_rtas_sensitivity.json
"""
import json
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import f_oneway
import statsmodels.formula.api as smf

ROOT = Path(r'D:/vc-task/RTAS_FINAL_PROJECT')
FIN = ROOT / '03_FINAL_ANALYSIS' / 'hlm' / 'within_unit_rtas'
FIN.mkdir(parents=True, exist_ok=True)
p = pd.read_csv(ROOT / '01_DATA' / 'final_analysis' / 'table5_project_dataset_n3714_full.csv')

# --- within-unit-year z-score (sample SD, ddof=1; cells with n<2 -> NaN) ---
g = p.groupby(['college', 'year'])['rtas']
mu = g.transform('mean')
sd = g.transform(lambda s: s.std(ddof=1))
cnt = g.transform('count')
p['rtas_z'] = np.where((cnt >= 2) & (sd > 0), (p['rtas'] - mu) / sd, np.nan)
n_undef = int(p['rtas_z'].isna().sum())
undef_cells = p.loc[p['rtas_z'].isna(), ['college', 'year']].drop_duplicates()
print(f'[within-unit] undefined z cells: {n_undef} project(s) in {len(undef_cells)} cell(s)')
for _, r in undef_cells.iterrows():
    print(f"    {r['college']} {int(r['year'])}")

# --- RQ1 re-run on z-scored RTAS (project-level one-way ANOVA) ---
lab = {1: 'university', 2: 'provincial', 3: 'national'}
grp = {k: p.loc[(p['level_code'] == k) & p['rtas_z'].notna(), 'rtas_z'].values for k in lab}
F, pF = f_oneway(*grp.values())
allv = np.concatenate(list(grp.values()))
eta2 = sum(len(v) * (v.mean() - allv.mean()) ** 2 for v in grp.values()) / ((allv - allv.mean()) ** 2).sum()
print(f'\n[RQ1-z] means univ/prov/natl = {grp[1].mean():+.4f}/{grp[2].mean():+.4f}/{grp[3].mean():+.4f}')
print(f'[RQ1-z] ANOVA F(2,{len(allv)-3}) = {F:.2f}, p = {pF:.2e}, eta2 = {eta2:.4f}')

# --- RQ3 v2b re-run on z-scored RTAS ---
p['is_provincial'] = (p['level_code'] == 2).astype(int)
p['is_national'] = (p['level_code'] == 3).astype(int)
p['year_centered'] = pd.to_numeric(p['year'], errors='coerce').astype(float) - 2022.0
p['log_prior3y'] = np.log1p(pd.to_numeric(p['advisor_prior_3y_works_mean'], errors='coerce'))
p['log_prior_supervision'] = np.log1p(pd.to_numeric(p['advisor_prior_supervised_projects'], errors='coerce'))
sub = p.dropna(subset=['rtas_z', 'is_provincial', 'is_national', 'year_centered',
                       'log_prior3y', 'log_prior_supervision', 'college']).copy()
md = smf.mixedlm('rtas_z ~ is_provincial + is_national + year_centered + log_prior3y + log_prior_supervision',
                 sub, groups=sub['college'])
res = md.fit(reml=True, method='lbfgs', maxiter=2000)
vg = float(res.cov_re.iloc[0, 0]); icc = vg / (vg + res.scale)
print(f'\n[RQ3-z] n={len(sub)}, units={sub.college.nunique()}, ICC={icc:.4f}')
for term in ['is_provincial', 'is_national', 'year_centered', 'log_prior3y', 'log_prior_supervision']:
    b, se, pv = res.params[term], res.bse[term], res.pvalues[term]
    print(f'  {term:24s} beta={b:+.6f} se={se:.6f} p={pv:.3e}')

# frozen reference values (raw RTAS, for the JSON comparison block)
frozen = {
    'RQ1': {'means': {'university': 0.121186, 'provincial': 0.139055, 'national': 0.146027},
            'F': 35.716, 'p': 4.326e-16, 'eta2': 0.018885},
    'RQ3': {'n': 3231, 'units': 39, 'ICC': 0.7376,
            'beta': {'is_provincial': 0.000615, 'is_national': -0.001624, 'year_centered': 0.003132,
                     'log_prior3y': 0.004266, 'log_prior_supervision': -0.006287}},
}
out = {
    'date': '2026-10-05', 'purpose': 'within-unit-year calibration sensitivity (college x year z-score)',
    'design_guardrail': 'removes between-unit-year baselines only; within-cell disciplinary titling remains',
    'n_undefined_z': n_undef,
    'undefined_cells': undef_cells.to_dict('records'),
    'frozen_raw_rtas': frozen,
    'z_scored': {
        'RQ1': {'n': int(len(allv)),
                'means': {lab[k]: float(grp[k].mean()) for k in lab},
                'F': float(F), 'p': float(pF), 'eta2': float(eta2)},
        'RQ3': {'n': int(len(sub)), 'units': int(sub.college.nunique()), 'ICC': float(icc),
                'terms': {t: {'beta': float(res.params[t]), 'se': float(res.bse[t]),
                              'p': float(res.pvalues[t])} for t in res.params.index if t != 'Intercept'}},
    },
}
with open(FIN / 'within_unit_rtas_sensitivity.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f'\n[done] wrote {FIN}/within_unit_rtas_sensitivity.json')
