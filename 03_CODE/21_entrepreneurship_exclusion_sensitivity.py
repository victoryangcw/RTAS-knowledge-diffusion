# -*- coding: utf-8 -*-
"""21 — Entrepreneurship-project exclusion sensitivity (post-audit A1).

CONTEXT (2026-09-22 raw-registry audit, script 20)
  The official 2021-2024 WHU ITTP registries carry a project-type field;
  158 UNIQUE entrepreneurship projects (创业训练/创业实践) are present in the
  frozen 3,714-row analytic dataset (4.25%; by year 74/23/26/35). The audit's
  raw row count was 160 because two 2024 titles are duplicated rows in the
  official registry itself; each appears once in the frozen dataset.
  The only 创业训练项目(北斗+专项) record belongs to an excluded college and
  is not in the frozen dataset. No official 2020 registry exists, so 2020
  types cannot be recovered and this sensitivity excludes ONLY the 158
  officially-typed 2021-2024 entrepreneurship projects.

WHAT THIS SCRIPT DOES
  1. Flags frozen projects by (year, normalized-title) join to the parsed
     official registries (03_FINAL_ANALYSIS/raw_registry_parsed_2021_2024.csv,
     produced by script 20; exact types 创业训练项目/创业实践项目).
  2. Descriptive contrast: RTAS mean/SD entrepreneurship vs innovation,
     Welch t-test, Cohen d (pooled SD); counts by year and funding tier.
  3. Refits the FROZEN v2b MixedLM
       rtas ~ is_provincial + is_national + year_centered
              + log_prior3y + log_prior_supervision
     groups=college, REML — once on the full complete-case sample (reproduces
     the frozen n=3,231 / ICC=0.7376 primary) and once after excluding the 160
     flagged projects. Covariates are taken from the frozen dataset unchanged
     (only the estimation sample changes).
  4. Writes coefficient comparison CSV + an aggregate JSON (no names/titles).

PROVENANCE
  01_DATA/final_analysis/table5_project_dataset_n3714_full.csv
  03_FINAL_ANALYSIS/raw_registry_parsed_2021_2024.csv (script 20; private)
    --> 03_FINAL_ANALYSIS/hlm/entrepreneurship_exclusion/
        hlm_excl_entrepreneurship_comparison.csv
        hlm_excl_entrepreneurship_summary.json
"""
from __future__ import annotations

import json
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats as sstats

warnings.filterwarnings('ignore')

ROOT = Path(r'D:/vc-task/RTAS_FINAL_PROJECT').resolve()
FROZEN = ROOT / '01_DATA' / 'final_analysis' / 'table5_project_dataset_n3714_full.csv'
PARSED = ROOT / '03_FINAL_ANALYSIS' / 'raw_registry_parsed_2021_2024.csv'
OUT = ROOT / '03_FINAL_ANALYSIS' / 'hlm' / 'entrepreneurship_exclusion'
OUT.mkdir(parents=True, exist_ok=True)


def norm_title(s):
    """Same normalisation as script 20."""
    if pd.isna(s):
        return ''
    s = str(s)
    s = s.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    s = re.sub(r'\s+', '', s)
    s = s.replace('——', '—').replace('－', '-').replace('（', '(').replace('）', ')')
    return s.strip(' "\'.,，。;；、')


# ---------- 1. flag entrepreneurship projects ----------
df = pd.read_csv(FROZEN)
assert len(df) == 3714, len(df)
df['ntitle'] = df['project_title'].apply(norm_title)

reg = pd.read_csv(PARSED)
ent_keys = set(
    reg.loc[reg['type'].isin(['创业训练项目', '创业实践项目']),
            ['year', 'ntitle']]
    .itertuples(index=False, name=None)
)
df['is_entrepreneurship'] = df.apply(
    lambda r: (int(r['year']), r['ntitle']) in ent_keys, axis=1)
n_ent = int(df['is_entrepreneurship'].sum())
print(f'Entrepreneurship projects flagged in frozen dataset: {n_ent}')
assert n_ent == 158, f'expected 158 unique projects from audit, got {n_ent}'

by_year = (df.groupby('year')['is_entrepreneurship'].sum().astype(int)
           .to_dict())
by_level = (df.groupby('level_code')['is_entrepreneurship'].sum().astype(int)
            .to_dict())
print('by year:', by_year)
print('by level_code (1=univ,2=prov,3=natl):', by_level)

# ---------- 2. descriptive RTAS contrast ----------
ent = df.loc[df['is_entrepreneurship'], 'rtas'].dropna().astype(float)
inn = df.loc[~df['is_entrepreneurship'], 'rtas'].dropna().astype(float)
t_stat, p_welch = sstats.ttest_ind(ent, inn, equal_var=False)
n1, n2 = len(ent), len(inn)
m1, m2 = float(ent.mean()), float(inn.mean())
s1, s2 = float(ent.std(ddof=1)), float(inn.std(ddof=1))
sp = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
cohen_d = (m1 - m2) / sp
print(f'\nEntrepreneurship n={n1} mean={m1:.4f} sd={s1:.4f}')
print(f'Innovation       n={n2} mean={m2:.4f} sd={s2:.4f}')
print(f'Welch t={t_stat:.3f} p={p_welch:.3e}; Cohen d={cohen_d:.3f}')

# ---------- 3. refit frozen v2b MixedLM spec on both samples ----------
df['is_provincial'] = df['level'].astype(str).str.contains('省级|Provincial', regex=True).astype(int)
df['is_national'] = df['level'].astype(str).str.contains('国家级|National', regex=True).astype(int)
df['year_centered'] = df['year'] - 2022
df['log_prior3y'] = np.log1p(pd.to_numeric(df['advisor_prior_3y_works_mean'], errors='coerce'))
df['log_prior_supervision'] = np.log1p(
    pd.to_numeric(df['advisor_prior_supervised_projects'], errors='coerce'))

FORMULA = ('rtas ~ is_provincial + is_national + year_centered '
           '+ log_prior3y + log_prior_supervision')
TERMS = ['Intercept', 'is_provincial', 'is_national', 'year_centered',
         'log_prior3y', 'log_prior_supervision']


def fit(sub):
    sub = sub.dropna(subset=['rtas', 'log_prior3y', 'log_prior_supervision',
                             'is_provincial', 'is_national',
                             'year_centered', 'college'])
    md = smf.mixedlm(FORMULA, sub, groups=sub['college'])
    res = md.fit(reml=True, method='lbfgs', maxiter=2000)
    var_g = float(res.cov_re.iloc[0, 0]) if res.cov_re.size else 0.0
    var_e = float(res.scale)
    icc = var_g / (var_g + var_e)
    out = {'n_obs': int(len(sub)),
           'n_colleges': int(sub['college'].nunique()),
           'var_college': var_g, 'var_resid': var_e, 'icc': icc,
           'coef': {}, 'se': {}, 'p': {}}
    for term in TERMS:
        if term in res.params.index:
            out['coef'][term] = float(res.params[term])
            out['se'][term] = float(res.bse[term])
            out['p'][term] = float(res.pvalues[term])
    return out


print('\n--- primary (full frozen sample) ---')
primary = fit(df)
print(f"n={primary['n_obs']} colleges={primary['n_colleges']} ICC={primary['icc']:.4f}")

print('\n--- sensitivity (entrepreneurship excluded) ---')
restricted = fit(df.loc[~df['is_entrepreneurship']].copy())
print(f"n={restricted['n_obs']} colleges={restricted['n_colleges']} "
      f"ICC={restricted['icc']:.4f}")

# ---------- 4. comparison CSV + JSON ----------
rows = []
for term in TERMS:
    if term not in primary['coef']:
        continue
    rows.append({
        'term': term,
        'primary_coef': primary['coef'][term],
        'primary_se': primary['se'][term],
        'primary_p': primary['p'][term],
        'excl_entre_coef': restricted['coef'][term],
        'excl_entre_se': restricted['se'][term],
        'excl_entre_p': restricted['p'][term],
        'coef_delta': restricted['coef'][term] - primary['coef'][term],
        'sign_agrees': np.sign(primary['coef'][term]) ==
                       np.sign(restricted['coef'][term]),
        'both_sig_05': (primary['p'][term] < 0.05) and
                       (restricted['p'][term] < 0.05),
    })
cmp_df = pd.DataFrame(rows)
cmp_df.to_csv(OUT / 'hlm_excl_entrepreneurship_comparison.csv',
              index=False, encoding='utf-8-sig')
print('\n' + cmp_df.round(6).to_string(index=False))

summary = {
    'description': 'A1 sensitivity: exclude 158 unique officially-typed '
                   'entrepreneurship projects (2021-2024) from the frozen '
                   'v2b MixedLM; 2020 types unavailable (no official registry).',
    'n_flagged_entrepreneurship': n_ent,
    'flagged_by_year': {str(k): int(v) for k, v in by_year.items()},
    'flagged_by_level_code': {str(k): int(v) for k, v in by_level.items()},
    'rtas_entrepreneurship': {'n': n1, 'mean': m1, 'sd': s1},
    'rtas_innovation': {'n': n2, 'mean': m2, 'sd': s2},
    'welch_t': float(t_stat), 'welch_p': float(p_welch),
    'cohen_d_pooled': float(cohen_d),
    'formula': FORMULA,
    'model': 'statsmodels MixedLM random intercept on college, REML, lbfgs',
    'primary': primary,
    'excl_entrepreneurship': restricted,
    'note': 'Covariates taken from the frozen dataset unchanged; only the '
            'estimation sample changes.',
}
(OUT / 'hlm_excl_entrepreneurship_summary.json').write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nDONE. Outputs in {OUT}')
