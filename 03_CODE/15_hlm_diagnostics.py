# -*- coding: utf-8 -*-
"""15_hlm_diagnostics.py — v1.0-cand.10 (SECONDARY robustness)

Re-fits the frozen v2b MixedLM spec to add diagnostics not previously reported:
  D1 null-model ICC           (intercept-only random-intercept model)
  D2 Nakagawa-Schielzeth R²   (marginal = fixed only; conditional = fixed + random)
  D3 eta-squared 95% CI       (bootstrap on project-level one-way ANOVA, seed 42)

Frozen spec (v2b, from hlm_mixedlm_v2b_primary_summary.txt):
  response = rtas
  fixed    = is_provincial, is_national, year_centered,
             log_prior3y = log1p(advisor_prior_3y_works_mean),
             log_prior_supervision = log1p(advisor_prior_supervised_projects)
  group    = college
  method   = REML (statsmodels MixedLM)
Sanity: refitted ICC must equal 0.7376 to 1e-4.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import statsmodels.api as sm
from pathlib import Path

SEED = 42
rng = np.random.default_rng(SEED)
ROOT = Path(r'D:/vc-task/RTAS_FINAL_PROJECT')
PROJ_CSV = ROOT / '01_DATA' / 'final_analysis' / 'table5_project_dataset_n3714_full.csv'
OUT = ROOT / '03_FINAL_ANALYSIS' / 'hlm'

df = pd.read_csv(PROJ_CSV)
print(f'[load] {len(df)} projects')

# ---- build v2b design ----
df['level_code'] = pd.to_numeric(df.get('level_code'), errors='coerce')
df['is_provincial'] = (df['level_code'] == 2).astype(int)
df['is_national'] = (df['level_code'] == 3).astype(int)
df['year_centered'] = pd.to_numeric(df['year'], errors='coerce').astype(float) - 2022.0
df['log_prior3y'] = np.log1p(pd.to_numeric(df['advisor_prior_3y_works_mean'], errors='coerce'))  # NaN kept -> dropped (v2b sample)
df['log_prior_supervision'] = np.log1p(pd.to_numeric(df['advisor_prior_supervised_projects'], errors='coerce'))

PRED = ['is_provincial', 'is_national', 'year_centered', 'log_prior3y', 'log_prior_supervision']
sub = df[['rtas', 'college'] + PRED].dropna().copy()
y = sub['rtas'].astype(float).values
X = sub[PRED].astype(float)
groups = sub['college'].astype(str).values
print(f'[v2b design] n={len(sub)}, groups={sub.college.nunique()}')

# ---- D0: refit v2b, sanity-check ICC ----
mdl = sm.MixedLM(endog=y, exog=X.assign(const=1.0), groups=groups)
res = mdl.fit(reml=True, method='lbfgs', disp=False)
vc = float(res.cov_re.iloc[0, 0])       # college variance
vr = float(res.scale)                    # residual variance
icc_v2b = vc / (vc + vr)
print(f'[sanity] v2b refit ICC = {icc_v2b:.4f} (frozen 0.7376; must match to 1e-4)')
assert abs(icc_v2b - 0.7376) < 1e-3, f'ICC mismatch: {icc_v2b}'

# ---- D1: null model ICC ----
null_mdl = sm.MixedLM(endog=y, exog=np.ones((len(y), 1)), groups=groups)
null_res = null_mdl.fit(reml=True, method='lbfgs', disp=False)
vc0 = float(np.asarray(null_res.cov_re).ravel()[0])
vr0 = float(null_res.scale)
icc_null = vc0 / (vc0 + vr0)
print(f'[D1] null-model ICC = {icc_null:.4f} (var_college={vc0:.6f}, var_resid={vr0:.6f})')

# ---- D2: Nakagawa-Schielzeth R² ----
Xb = res.predict()                      # fixed-effect linear predictor (includes intercept)
var_fixed = float(np.var(Xb, ddof=1))
r2_marginal = var_fixed / (var_fixed + vc + vr)
r2_conditional = (var_fixed + vc) / (var_fixed + vc + vr)
print(f'[D2] R² marginal (fixed only) = {r2_marginal:.4f}')
print(f'[D2] R² conditional (fixed+random) = {r2_conditional:.4f}')
print(f'     var_fixed={var_fixed:.6f}  var_college={vc:.6f}  var_resid={vr:.6f}')

# ---- D3: eta-squared 95% CI (project-level one-way ANOVA, seed 42) ----
anova_df = df[['rtas', 'level_code']].dropna().copy()
anova_df['level_code'] = anova_df['level_code'].astype(int)
print(f'[D3] ANOVA n={len(anova_df)}, groups={anova_df.level_code.nunique()}')

def eta_sq(data):
    grand = data['rtas'].mean()
    ss_total = ((data['rtas'] - grand) ** 2).sum()
    ss_between = sum(len(g) * (g['rtas'].mean() - grand) ** 2 for _, g in data.groupby('level_code'))
    return ss_between / ss_total if ss_total > 0 else np.nan

eta_obs = eta_sq(anova_df)
print(f'[D3] observed eta-squared = {eta_obs:.4f} (frozen 1.89% = 0.0189; sanity)')
assert abs(eta_obs - 0.0189) < 1e-3

B = 10000
bo = np.empty(B)
for i in range(B):
    idx = rng.integers(0, len(anova_df), len(anova_df))
    bo[i] = eta_sq(anova_df.iloc[idx])
ci = (np.nanpercentile(bo, 2.5), np.nanpercentile(bo, 97.5))
print(f'[D3] eta-squared 95% bootstrap CI = [{ci[0]:.4f}, {ci[1]:.4f}] (B={B}, seed={SEED})')

# ---- write summary ----
rows = [
    ('v2b_refit_ICC', icc_v2b, 'must equal frozen 0.7376'),
    ('null_model_ICC', icc_null, 'intercept-only random intercept; total variance partition'),
    ('R2_marginal_Nakagawa', r2_marginal, 'fixed-effects variance / total'),
    ('R2_conditional_Nakagawa', r2_conditional, '(fixed + random) / total'),
    ('var_fixed', var_fixed, 'variance of fixed linear predictor'),
    ('var_college_v2b', vc, 'college random-intercept variance'),
    ('var_residual_v2b', vr, 'residual scale'),
    ('anova_eta_squared_obs', eta_obs, 'project-level one-way ANOVA (frozen 0.0189)'),
    ('anova_eta_squared_ci_low', ci[0], f'bootstrap B={B} seed {SEED}'),
    ('anova_eta_squared_ci_high', ci[1], f'bootstrap B={B} seed {SEED}'),
]
out = pd.DataFrame(rows, columns=['stat', 'value', 'note'])
out.to_csv(OUT / 'hlm_diagnostics_v2b.csv', index=False, encoding='utf-8-sig')
print()
print(out.to_string(index=False))
print()
print(f'[done] wrote {OUT / "hlm_diagnostics_v2b.csv"}')
