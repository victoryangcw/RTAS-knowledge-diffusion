# -*- coding: utf-8 -*-
"""18_advisor_dependence_sensitivity.py — v1.0-cand.14 (SECONDARY sensitivity)

Advisor-level dependence sensitivity for the RQ3 MixedLM.
================================================================
MOTIVATION:
  Primary v2b model has only a college random intercept. Advisors supervise
  repeated projects (18.8% of individual advisors supervise >=4), so
  residual dependence within advisors is not explicitly modeled. This is
  acknowledged in Limitations but never tested.

DESIGN CHOICE (multiple membership):
  528 projects have >=2 advisors. (1|college)+(1|advisor) on expanded rows
  would duplicate projects / change the data structure, and there is no
  primary-advisor flag in the administrative data. Cleanest approach:
  restrict to SINGLE-ADVISOR projects (advisor_count == 1, n=3,186 of 3,714),
  where the advisor random intercept is unambiguously defined, and fit:

    Model A (subset baseline):
      rtas ~ is_provincial + is_national + year_centered
             + log_prior3y + log_prior_supervision + (1|college)
    Model B (crossed):
      same fixed effects + (1|college) + (1|advisor)

  Comparing A vs B on the SAME observations isolates the effect of adding
  the advisor level; frozen primary (n=3,231) is shown for reference.

FALLBACK (if crossed MixedLM does not converge / boundary solution):
  College fixed effects (dummies) + advisor-clustered robust SE (OLS),
  same single-advisor subset.

HOMONYM GUARD (Model D):
  Same college-FE OLS but SEs clustered on college x normalized advisor name,
  so identical Chinese names appearing in different colleges are not merged
  into one cluster.

QUESTION:
  After explicitly accounting for repeated observations within advisors,
  do the substantive fixed-effect conclusions materially change?

OUTPUTS:
  03_FINAL_ANALYSIS/hlm/advisor_dependence/
    advisor_dependence_coefficients.csv   (3-way coefficient comparison)
    advisor_dependence_summary.json
    advisor_dependence_summary.txt
"""
import warnings; warnings.filterwarnings('ignore')
import re, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJ = Path(r'D:/vc-task/RTAS_FINAL_PROJECT')
T5 = PROJ / '01_DATA' / 'final_analysis' / 'table5_project_dataset_n3714_full.csv'
OUT = PROJ / '03_FINAL_ANALYSIS' / 'hlm' / 'advisor_dependence'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 42; np.random.seed(SEED)

FROZEN_PRIMARY = {  # hlm_mixedlm_v2b_primary_coefficients.csv, n=3231
    'n': 3231, 'n_colleges': 39, 'icc': 0.7376,
    'r2_marginal': 0.0075, 'r2_conditional': 0.7395,
}

t0 = time.time()

# ============================================================
# 1. Build single-advisor subset with v2b covariates
# ============================================================
print('='*60)
print('[1] Loading data and building single-advisor subset...')
df = pd.read_csv(T5)
assert len(df) == 3714

def split_advisors(s):
    if not isinstance(s, str): return []
    parts = re.split(r'[、，,;；]', s)
    return [p.strip() for p in parts if p.strip()]

df['adv_atoms'] = df['advisor'].apply(split_advisors)
df['n_atoms'] = df['adv_atoms'].apply(len)
single = df[df['advisor_count'] == 1].copy()
single['advisor_id'] = single['adv_atoms'].str[0]
print(f'  single-advisor projects: {len(single)} / {len(df)}')
print(f'  multi-advisor excluded: {(df["advisor_count"]>1).sum()}')

single['is_provincial'] = single['level'].astype(str).str.contains('省级|Provincial', regex=True).astype(int)
single['is_national'] = single['level'].astype(str).str.contains('国家级|National', regex=True).astype(int)
single['year_centered'] = pd.to_numeric(single['year'], errors='coerce') - 2022
single['log_prior3y'] = np.log1p(pd.to_numeric(single['advisor_prior_3y_works_mean'], errors='coerce'))
single['log_prior_supervision'] = np.log1p(pd.to_numeric(single['advisor_prior_supervised_projects'], errors='coerce'))

need = ['rtas', 'college', 'advisor_id', 'is_provincial', 'is_national',
        'year_centered', 'log_prior3y', 'log_prior_supervision']
d = single.dropna(subset=need).copy()

n_proj = len(d)
n_colleges = d['college'].nunique()
n_advisors = d['advisor_id'].nunique()
loads = d.groupby('advisor_id').size()
n_repeat_advisors = int((loads >= 2).sum())
n_projects_repeat_advisors = int(loads[loads >= 2].sum())
print(f'  complete cases: {n_proj}')
print(f'  colleges: {n_colleges}')
print(f'  individual advisors: {n_advisors}')
print(f'  advisors with >=2 projects in subset: {n_repeat_advisors} '
      f'(covering {n_projects_repeat_advisors} projects)')

FORMULA = ('rtas ~ is_provincial + is_national + year_centered '
           '+ log_prior3y + log_prior_supervision')

def co_table(res):
    ci = res.conf_int()
    co = pd.DataFrame({
        'term': res.params.index,
        'coef': res.params.values,
        'se': res.bse.values,
        'z': res.tvalues.values,
        'p': res.pvalues.values,
        'ci_low': ci[0].values,
        'ci_high': ci[1].values,
    })
    co['stars'] = np.where(co['p'] < 0.001, '***',
                   np.where(co['p'] < 0.01, '**',
                   np.where(co['p'] < 0.05, '*', 'ns')))
    return co

def r2_nakagawa(res, md, data):
    """Marginal/conditional R2 for (possibly VC) Gaussian MixedLM."""
    var_g = float(res.cov_re.iloc[0, 0]) if res.cov_re.size else 0.0
    var_vc = float(np.sum(res.vcomp)) if hasattr(res, 'vcomp') and len(res.vcomp) else 0.0
    var_e = float(res.scale)
    var_fixed = float(np.var(md.exog @ res.fe_params))
    denom = var_fixed + var_g + var_vc + var_e
    return {
        'var_college': var_g, 'var_advisor': var_vc, 'var_resid': var_e,
        'icc_college': var_g / denom,
        'icc_advisor': var_vc / denom,
        'icc_clustered': (var_g + var_vc) / denom,
        'r2_marginal': var_fixed / denom,
        'r2_conditional': (var_fixed + var_g + var_vc) / denom,
    }

# ============================================================
# 2. Model A: college-only RI on the single-advisor subset
# ============================================================
print('\n' + '='*60)
print('[2] Model A: college-only RI (single-advisor subset)')
mdA = smf.mixedlm(FORMULA, d, groups=d['college'])
resA = mdA.fit(reml=True, method='lbfgs', maxiter=5000)
coA = co_table(resA)
fitA = r2_nakagawa(resA, mdA, d)
print(f'  converged={resA.converged}  ICC_college={fitA["icc_college"]:.4f}')
print(coA.round(6).to_string(index=False))

# ============================================================
# 3. Model B: crossed college + advisor random intercepts
# ============================================================
print('\n' + '='*60)
print('[3] Model B: crossed (1|college) + (1|advisor) via vc_formula')
crossed_ok = False
try:
    mdB = smf.mixedlm(FORMULA, d, groups=d['college'],
                      vc_formula={'advisor': '0 + C(advisor_id)'})
    try:
        resB = mdB.fit(reml=True, method='lbfgs', maxiter=5000)
    except Exception:
        resB = mdB.fit(reml=True, method='cg', maxiter=10000)
    coB = co_table(resB)
    fitB = r2_nakagawa(resB, mdB, d)
    crossed_ok = bool(resB.converged)
    print(f'  converged={resB.converged}')
    print(f'  var_college={fitB["var_college"]:.6f}  var_advisor={fitB["var_advisor"]:.6f}  '
          f'var_resid={fitB["var_resid"]:.6f}')
    print(f'  ICC_college={fitB["icc_college"]:.4f}  ICC_advisor={fitB["icc_advisor"]:.4f}  '
          f'ICC_clustered={fitB["icc_clustered"]:.4f}')
    print(f'  marginal R2={fitB["r2_marginal"]:.4f}  conditional R2={fitB["r2_conditional"]:.4f}')
    print(coB.round(6).to_string(index=False))
except Exception as e:
    import traceback; traceback.print_exc()
    print(f'[CROSSED FAILED] {type(e).__name__}: {e}')

# ============================================================
# 4. Fallback / robustness: college FE + advisor-clustered robust SE
#    ALWAYS run — even if the crossed fit formally converged, a boundary
#    solution (var_college = 0) with unstable coefficients is not reliable.
# ============================================================
print('\n' + '='*60)
print('[4] College FE OLS + advisor-clustered robust SE')
import statsmodels.api as sm
mm = smf.ols(FORMULA + ' + C(college)', data=d)
resC = mm.fit(cov_type='cluster', cov_kwds={'groups': d['advisor_id']})
ciC = resC.conf_int()
coC = pd.DataFrame({
    'term': resC.params.index,
    'coef': resC.params.values,
    'se': resC.bse.values,
    'z': resC.tvalues.values,
    'p': resC.pvalues.values,
    'ci_low': ciC[0].values,
    'ci_high': ciC[1].values,
})
coC['stars'] = np.where(coC['p'] < 0.001, '***',
                np.where(coC['p'] < 0.01, '**',
                np.where(coC['p'] < 0.05, '*', 'ns')))
fitC = {'n': n_proj, 'model': 'OLS college FE, SE clustered by advisor'}
print(coC[~coC['term'].str.startswith('C(college)')].round(6).to_string(index=False))

# ------------------------------------------------------------
# 4b. Cluster-ID check: college x normalized advisor name
#     Guards against identical Chinese names across colleges
#     (homonyms) being merged into one advisor cluster.
# ------------------------------------------------------------
print('\n' + '='*60)
print('[4b] College FE OLS, SE clustered by college x advisor-name ID')
d['cluster_id_cxa'] = (d['college'].astype(str).str.strip()
                       + '||' + d['advisor_id'].astype(str).str.strip())
n_clusters_raw = int(d['advisor_id'].nunique())
n_clusters_cxa = int(d['cluster_id_cxa'].nunique())
mmD = smf.ols(FORMULA + ' + C(college)', data=d)
resD = mmD.fit(cov_type='cluster', cov_kwds={'groups': d['cluster_id_cxa']})
ciD = resD.conf_int()
coD = pd.DataFrame({
    'term': resD.params.index,
    'coef': resD.params.values,
    'se': resD.bse.values,
    'z': resD.tvalues.values,
    'p': resD.pvalues.values,
    'ci_low': ciD[0].values,
    'ci_high': ciD[1].values,
})
coD['stars'] = np.where(coD['p'] < 0.001, '***',
                np.where(coD['p'] < 0.01, '**',
                np.where(coD['p'] < 0.05, '*', 'ns')))
fitD = {'n': n_proj,
        'model': 'OLS college FE, SE clustered by college x advisor-name',
        'n_clusters_raw_advisor_name': n_clusters_raw,
        'n_clusters_college_x_advisor': n_clusters_cxa}
print(f'  clusters: raw advisor name = {n_clusters_raw}; '
      f'college x advisor = {n_clusters_cxa}')
print(coD[~coD['term'].str.startswith('C(college)')].round(6).to_string(index=False))

boundary = crossed_ok and (fitB['var_college'] < 1e-10)
if boundary:
    print('\n[NOTE] Crossed fit is a BOUNDARY solution (var_college=0); '
          'advisor-level covariates vary mainly between advisors (within-SD '
          '18% of total), so crossed RE coefficients are unstable. '
          'Model C is the reliable sensitivity.')

# ============================================================
# 5. Three-way coefficient comparison (frozen primary / A / B)
# ============================================================
print('\n' + '='*60)
print('[5] Coefficient comparison')
fp = pd.read_csv(PROJ / '03_FINAL_ANALYSIS' / 'hlm' /
                 'hlm_mixedlm_v2b_primary_coefficients.csv')
fp = fp.rename(columns={'estimate': 'coef', 'std_error': 'se', 'p_value': 'p',
                        'ci_95_lo': 'ci_low', 'ci_95_hi': 'ci_high',
                        'significance_mark': 'stars'})
fp = fp[['term', 'coef', 'se', 'p', 'ci_low', 'ci_high', 'stars']]

cmp = fp.merge(coA, on='term', suffixes=('_primary', '_subset_college'), how='outer')
if crossed_ok:
    cmp = cmp.merge(coB.rename(columns={
        'coef': 'coef_crossed', 'se': 'se_crossed', 'z': 'z_crossed',
        'p': 'p_crossed', 'ci_low': 'ci_low_crossed', 'ci_high': 'ci_high_crossed',
        'stars': 'stars_crossed'}), on='term', how='outer')
    cmp['delta_crossed_vs_subset'] = cmp['coef_crossed'] - cmp['coef_subset_college']
    cmp['delta_crossed_vs_primary'] = cmp['coef_crossed'] - cmp['coef_primary']
    # CI still excludes zero in crossed model?
    cmp['ci_excludes_zero_crossed'] = ((cmp['ci_low_crossed'] > 0) & (cmp['ci_high_crossed'] > 0)) | \
                                      ((cmp['ci_low_crossed'] < 0) & (cmp['ci_high_crossed'] < 0))
# Always attach college-FE + advisor-clustered results
cc = coC.rename(columns={
    'coef': 'coef_collegeFE_advCluster', 'se': 'se_feCluster', 'z': 'z_feCluster',
    'p': 'p_feCluster', 'ci_low': 'ci_low_feCluster', 'ci_high': 'ci_high_feCluster',
    'stars': 'stars_feCluster'})
cmp = cmp.merge(cc, on='term', how='outer')
cmp['delta_feCluster_vs_primary'] = cmp['coef_collegeFE_advCluster'] - cmp['coef_primary']
cmp['ci_excludes_zero_feCluster'] = ((cmp['ci_low_feCluster'] > 0) & (cmp['ci_high_feCluster'] > 0)) | \
                                    ((cmp['ci_low_feCluster'] < 0) & (cmp['ci_high_feCluster'] < 0))
# Attach college x advisor-name clustered results (homonym guard)
cdx = coD.rename(columns={
    'coef': 'coef_collegeFE_cxaCluster', 'se': 'se_cxaCluster', 'z': 'z_cxaCluster',
    'p': 'p_cxaCluster', 'ci_low': 'ci_low_cxaCluster', 'ci_high': 'ci_high_cxaCluster',
    'stars': 'stars_cxaCluster'})
cmp = cmp.merge(cdx, on='term', how='outer')

keep_terms = ['Intercept', 'is_provincial', 'is_national', 'year_centered',
              'log_prior3y', 'log_prior_supervision']
cmp = cmp[cmp['term'].isin(keep_terms)].reset_index(drop=True)
print(cmp.round(6).to_string(index=False))
cmp.to_csv(OUT / 'advisor_dependence_coefficients.csv', index=False, encoding='utf-8-sig')

# ============================================================
# 6. Summary JSON / TXT
# ============================================================
summary = {
    'design': ('single-advisor projects only (advisor_count==1); '
               'college RI vs college+advisor crossed RI on identical cases; '
               'college FE + advisor-clustered SE as robust fallback'),
    'n_projects_single_advisor_total': int(len(single)),
    'n_multi_advisor_excluded': int((df['advisor_count'] > 1).sum()),
    'n_complete_cases': int(n_proj),
    'n_colleges': int(n_colleges),
    'n_advisors': int(n_advisors),
    'n_advisors_with_ge2_projects': n_repeat_advisors,
    'n_projects_under_repeat_advisors': n_projects_repeat_advisors,
    'structure_diagnostics': {
        'advisors_appearing_in_multiple_colleges': int(
            (single.groupby('advisor_id')['college'].nunique() > 1).sum()),
        'note': ('crossing is partly artificial (identical Chinese names '
                 'across colleges were not disambiguated)'),
    },
    'frozen_primary_n3231': FROZEN_PRIMARY,
    'model_A_subset_college_only': {
        'converged': bool(resA.converged), **fitA,
    },
    'model_B_crossed': None,
    'model_C_collegeFE_advisor_clustered': {
        **fitC,
        'coefficients': {r['term']: {
            'coef': float(r['coef']), 'se': float(r['se']), 'p': float(r['p']),
            'ci': [float(r['ci_low']), float(r['ci_high'])], 'stars': r['stars']}
            for _, r in coC[~coC['term'].str.startswith('C(college)')].iterrows()},
    },
    'model_D_collegeFE_college_x_advisor_clustered': {
        **fitD,
        'coefficients': {r['term']: {
            'coef': float(r['coef']), 'se': float(r['se']), 'p': float(r['p']),
            'ci': [float(r['ci_low']), float(r['ci_high'])], 'stars': r['stars']}
            for _, r in coD[~coD['term'].str.startswith('C(college)')].iterrows()},
    },
}
if crossed_ok:
    key_terms = ['log_prior3y', 'log_prior_supervision', 'year_centered',
                 'is_provincial', 'is_national']
    modelB_coefs = {}
    for t in key_terms:
        r = coB[coB['term'] == t].iloc[0]
        modelB_coefs[t] = {
            'coef': float(r['coef']), 'se': float(r['se']), 'p': float(r['p']),
            'ci': [float(r['ci_low']), float(r['ci_high'])],
            'stars': r['stars'],
        }
    summary['model_B_crossed'] = {
        'converged': True, 'boundary_solution': bool(boundary), **fitB,
        'coefficients': modelB_coefs,
        'interpretation_warning': (
            'boundary solution (var_college=0) and 4x movement in '
            'log_prior3y: advisor-level covariates vary mainly BETWEEN '
            'advisors (within-advisor SD 18% of total for log_prior3y; '
            'constant within advisor for ~30% of repeat advisors), so '
            'crossed-RE fixed effects are not stably identified. Treat '
            'Model C as the reliable dependence sensitivity.') if boundary else '',
    }
    # headline deltas (crossed reference)
    b3 = coB.loc[coB.term == 'log_prior3y', 'coef'].iloc[0]
    a3 = coA.loc[coA.term == 'log_prior3y', 'coef'].iloc[0]
    p3 = fp.loc[fp.term == 'log_prior3y', 'coef'].iloc[0]
    c3 = coC.loc[coC.term == 'log_prior3y', 'coef'].iloc[0]
    d3v = coD.loc[coD.term == 'log_prior3y', 'coef'].iloc[0]
    summary['log_prior3y'] = {
        'frozen_primary': float(p3),
        'subset_college_only': float(a3),
        'crossed_college_advisor': float(b3),
        'collegeFE_advisor_clustered': float(c3),
        'collegeFE_college_x_advisor_clustered': float(d3v),
        'delta_crossed_minus_subset': float(b3 - a3),
        'delta_crossed_minus_primary': float(b3 - p3),
        'delta_feCluster_minus_primary': float(c3 - p3),
        'delta_cxaCluster_minus_primary': float(d3v - p3),
    }
else:
    a3 = coA.loc[coA.term == 'log_prior3y', 'coef'].iloc[0]
    p3 = fp.loc[fp.term == 'log_prior3y', 'coef'].iloc[0]
    c3 = coC.loc[coC.term == 'log_prior3y', 'coef'].iloc[0]
    d3v = coD.loc[coD.term == 'log_prior3y', 'coef'].iloc[0]
    summary['log_prior3y'] = {
        'frozen_primary': float(p3),
        'subset_college_only': float(a3),
        'collegeFE_advisor_clustered': float(c3),
        'collegeFE_college_x_advisor_clustered': float(d3v),
        'delta_feCluster_minus_primary': float(c3 - p3),
        'delta_cxaCluster_minus_primary': float(d3v - p3),
    }

with open(OUT / 'advisor_dependence_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

with open(OUT / 'advisor_dependence_summary.txt', 'w', encoding='utf-8') as f:
    f.write('Advisor-Level Dependence Sensitivity\n' + '='*60 + '\n\n')
    f.write(f'Single-advisor projects: {len(single)} / 3714; '
            f'complete cases n={n_proj}\n')
    f.write(f'Colleges: {n_colleges}; advisors: {n_advisors}; '
            f'advisors with >=2 projects: {n_repeat_advisors} '
            f'({n_projects_repeat_advisors} projects)\n\n')
    f.write('--- Model A: college-only RI, single-advisor subset ---\n')
    f.write(str(resA.summary()))
    f.write(f"\nICC_college={fitA['icc_college']:.4f}  "
            f"marg R2={fitA['r2_marginal']:.4f}  cond R2={fitA['r2_conditional']:.4f}\n\n")
    if crossed_ok:
        f.write('--- Model B: crossed (1|college)+(1|advisor) '
                f'{"[BOUNDARY SOLUTION — unreliable]" if boundary else ""}---\n')
        f.write(str(resB.summary()))
        f.write(f"\nvar_college={fitB['var_college']:.6f} var_advisor={fitB['var_advisor']:.6f} "
                f"var_resid={fitB['var_resid']:.6f}\n")
        f.write(f"ICC_college={fitB['icc_college']:.4f} ICC_advisor={fitB['icc_advisor']:.4f} "
                f"ICC_clustered={fitB['icc_clustered']:.4f}\n")
        f.write(f"marg R2={fitB['r2_marginal']:.4f}  cond R2={fitB['r2_conditional']:.4f}\n\n")
    f.write('--- Model C: college FE + advisor-clustered SE (reliable dependence check) ---\n')
    f.write(coC[~coC['term'].str.startswith('C(college)')].round(6).to_string(index=False))
    f.write(f'\n\n--- Model D: college FE + SE clustered by college x advisor-name '
            f'(homonym guard; clusters {n_clusters_raw} -> {n_clusters_cxa}) ---\n')
    f.write(coD[~coD['term'].str.startswith('C(college)')].round(6).to_string(index=False))
    f.write('\n\n--- Coefficient comparison ---\n')
    f.write(cmp.round(6).to_string(index=False))

print('\n' + '='*60)
print(f'[DONE] {time.time()-t0:.1f}s. Outputs in {OUT}')
if crossed_ok:
    lp = summary['log_prior3y']
    print(f"log_prior3y: primary={lp['frozen_primary']:+.6f}  "
          f"subset={lp['subset_college_only']:+.6f}  "
          f"crossed={lp['crossed_college_advisor']:+.6f}{'  [BOUNDARY]' if boundary else ''}  "
          f"collegeFE+advCluster={lp['collegeFE_advisor_clustered']:+.6f}  "
          f"collegeFE+cxaCluster={lp['collegeFE_college_x_advisor_clustered']:+.6f}")
