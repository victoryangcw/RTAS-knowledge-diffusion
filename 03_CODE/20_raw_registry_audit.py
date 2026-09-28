# -*- coding: utf-8 -*-
"""20_raw_registry_audit.py — Audit the ANALYTIC project dataset against the
ORIGINAL official WHU ITTP (大创) project-registry Excel files.

The earlier numerical provenance audit (19_numerical_provenance_audit.py)
verified every manuscript number against frozen/interim artifacts.  This audit
goes one step further UPSTREAM: it re-parses the official per-year registry
Excels as released by the university administration and checks:

  A1  Project TYPE: do the official registries contain entrepreneurship
      training/practice projects (创业训练/创业实践项目), and are any such
      projects present in the analytic 3,714 dataset?
  A2  Uniqueness: rows / unique titles / duplicates in the 3,887-row merged
      registry (五年所有题目.xlsx) and in the frozen 3,714 dataset.
  A3  Funding tier counts (国家级/省级/校级) by year and overall.
  A4  Advisor splitting: 1,834 individual advisors / 4,244 links / 528
      co-supervised projects, rebuilt from raw advisor strings.
  EX  3,887 -> 3,714: identify the 173 excluded rows and confirm the exclusion
      rule (8 colleges with no matched paper topics).

RAW SOURCES (not redistributed; kept outside the public repo):
  D:\\大创研究\\论文撰写——数据画像\\result\\code\\DataDrawings\\
    武汉大学2021年大学生创新创业训练计划项目拟立项名单.xlsx;.xlsx
    附件：武汉大学2022年大学生创新创业训练计划项目拟立项名单项.xlsx
    附件：武汉大学2023年大学生创新创业训练计划项目立项名单.xlsx
    附件：武汉大学2024年大学生创新创业训练计划立项项目名单（公示）.xlsx
    五年所有题目.xlsx
NOTE: no official 2020 registry Excel is available in the archive; 2020 rows
exist only in the merged 五年所有题目 table (no type field).
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(r'D:\大创研究\论文撰写——数据画像\result\code\DataDrawings')
FROZEN = Path(r'd:\vc-task\RTAS_FINAL_PROJECT\01_DATA\final_analysis'
              r'\table5_project_dataset_n3714_full.csv')
OUT_DIR = FROZEN.parents[2] / '03_FINAL_ANALYSIS'
OUT_DIR.mkdir(parents=True, exist_ok=True)

results = []


def check(item, ok, detail):
    results.append((item, 'PASS' if ok else 'FAIL', detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {item}: {detail}")


def norm_title(s):
    """Normalize a project title for matching."""
    if pd.isna(s):
        return ''
    s = str(s)
    s = s.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    s = re.sub(r'\s+', '', s)
    s = s.replace('——', '—').replace('－', '-').replace('（', '(').replace('）', ')')
    s = s.strip(' "\'.,，。;；、')
    return s


# ================================================================
# 1. Parse the four official per-year registries (2021-2024)
# ================================================================
def parse_registries():
    rows = []

    # ---- 2021: header at row index 1 ----
    p21 = RAW_DIR / '武汉大学2021年大学生创新创业训练计划项目拟立项名单.xlsx;.xlsx'
    d = pd.read_excel(p21, header=1)
    d = d.rename(columns={d.columns[0]: '序号'})
    for _, r in d.iterrows():
        if pd.isna(r.get('项目名称')):
            continue
        rows.append({'year': 2021, 'title': r['项目名称'], 'type': r.get('项目类型'),
                     'level': r.get('项目级别'), 'college': r.get('学院'),
                     'advisor': r.get('指导教师姓名'), 'pid': r.get('序号')})

    # ---- 2022: header at row index 1 ----
    p22 = RAW_DIR / '附件：武汉大学2022年大学生创新创业训练计划项目拟立项名单项.xlsx'
    d = pd.read_excel(p22, sheet_name='2022年拟立项项目', header=1)
    for _, r in d.iterrows():
        if pd.isna(r.get('项目名称')):
            continue
        rows.append({'year': 2022, 'title': r['项目名称'], 'type': r.get('项目类型'),
                     'level': r.get('项目级别'), 'college': r.get('所属学院'),
                     'advisor': r.get('指导教师'), 'pid': r.get('项目编号')})

    # ---- 2023: header at row index 1, main sheet ----
    p23 = RAW_DIR / '附件：武汉大学2023年大学生创新创业训练计划项目立项名单.xlsx'
    d = pd.read_excel(p23, sheet_name='武汉大学2023年大学生创新创业训练计划项目立项名单',
                      header=1)
    for _, r in d.iterrows():
        if pd.isna(r.get('项目名称')):
            continue
        rows.append({'year': 2023, 'title': r['项目名称'], 'type': r.get('项目类型'),
                     'level': r.get('项目级别'), 'college': r.get('项目所属单位'),
                     'advisor': r.get('指导教师'), 'pid': r.get('项目编号')})

    # ---- 2024: header at row index 2 (公示 sheet) + 遥感院33项 sheet (row 1) ----
    p24 = RAW_DIR / '附件：武汉大学2024年大学生创新创业训练计划立项项目名单（公示）.xlsx'
    d = pd.read_excel(p24, sheet_name='2024年立项公示', header=2)
    for _, r in d.iterrows():
        if pd.isna(r.get('项目名称')):
            continue
        rows.append({'year': 2024, 'title': r['项目名称'], 'type': r.get('项目类型'),
                     'level': r.get('项目级别'), 'college': r.get('项目所属单位'),
                     'advisor': r.get('指导教师'), 'pid': r.get('项目编号')})
    d2 = pd.read_excel(p24, sheet_name='遥感院33项', header=1)
    for _, r in d2.iterrows():
        if pd.isna(r.get('项目名称')):
            continue
        rows.append({'year': 2024, 'title': r['项目名称'], 'type': r.get('项目类型'),
                     'level': r.get('项目级别'), 'college': r.get('项目所属单位'),
                     'advisor': r.get('指导教师'), 'pid': r.get('项目编号')})

    reg = pd.DataFrame(rows)
    reg['type'] = reg['type'].astype(str).str.strip()
    reg['level'] = reg['level'].astype(str).str.strip()
    reg['ntitle'] = reg['title'].apply(norm_title)
    return reg


# ================================================================
# 2. Advisor string splitting (mirrors the frozen convention)
# ================================================================
SPLIT_RE = re.compile(r'[、,，;；/／\n\r]+|(?<=[\u4e00-\u9fa5])\s+(?=[\u4e00-\u9fa5])')


def split_advisors(s):
    if pd.isna(s):
        return []
    parts = [p.strip() for p in SPLIT_RE.split(str(s))]
    return [p for p in parts if p and p.lower() != 'nan']


def main():
    print('=' * 70)
    print('RAW REGISTRY AUDIT — official ITTP lists vs analytic 3,714 dataset')
    print('=' * 70)

    # ---- load frozen + merged ----
    fr = pd.read_csv(FROZEN)
    fr['ntitle'] = fr['project_title'].apply(norm_title)
    merged = pd.read_excel(RAW_DIR / '五年所有题目.xlsx')
    merged['ntitle'] = merged['项目名称'].apply(norm_title)

    reg = parse_registries()
    reg.to_csv(OUT_DIR / 'raw_registry_parsed_2021_2024.csv',
               index=False, encoding='utf-8-sig')

    # ---------- A1: project types in official registries ----------
    print('\n--- A1: project types in OFFICIAL registries (2021-2024) ---')
    ct = pd.crosstab(reg['year'], reg['type'], margins=True)
    print(ct.to_string())
    ent_types = ['创业训练项目', '创业实践项目']
    ent = reg[reg['type'].isin(ent_types)].copy()
    check('A1 official registries contain entrepreneurship projects',
          len(ent) > 0, f'{len(ent)} entrep. rows in 2021-2024 official lists')

    # match entrepreneurship rows into merged/frozen on the YEAR+title key
    # (cross-year same-title renewals must not be counted as matches)
    mkeys = set(zip(merged['年份'].astype(int), merged['ntitle']))
    fkeys = set(zip(fr['year'].astype(int), fr['ntitle']))
    ent['_in_merged'] = [(int(y), t) in mkeys for y, t in zip(ent['year'], ent['ntitle'])]
    ent['_in_frozen'] = [(int(y), t) in fkeys for y, t in zip(ent['year'], ent['ntitle'])]
    n_ent_merged = int(ent['_in_merged'].sum())
    n_ent_frozen = int(ent['_in_frozen'].sum())
    # official registry rows can be duplicated (two 2024 titles appear twice);
    # the frozen dataset holds each project once -> count UNIQUE projects too
    n_ent_frozen_unique = int(
        ent.loc[ent['_in_frozen'], ['year', 'ntitle']].drop_duplicates().shape[0])
    n_dup_rows = n_ent_frozen - n_ent_frozen_unique
    print(f'\nEntrepreneurship rows by year/type in frozen 3,714:')
    print(ent[ent['_in_frozen']].groupby(['year', 'type']).size().to_string())
    print('By level in frozen:')
    print(ent[ent['_in_frozen']]['level'].value_counts().to_string())
    print(f'OFFICIAL entrepreneurship rows 2021-24 = {len(ent)}; '
          f'in merged = {n_ent_merged}; in frozen 3,714 = {n_ent_frozen} rows '
          f'= {n_ent_frozen_unique} UNIQUE projects ({n_dup_rows} duplicate '
          f'registry rows: same title listed twice in the official list)')
    not_in_frozen = ent[~ent['_in_frozen']]
    print(f'Entrepreneurship rows NOT in frozen ({len(not_in_frozen)}):')
    print(not_in_frozen[['year', 'type', 'level', 'title', 'college']].to_string(index=False))
    check('A1 entrepreneurship projects inside MERGED 3,887 table',
          n_ent_merged == 0, f'{n_ent_merged} of {len(ent)} (year-keyed)')
    check('A1 entrepreneurship projects inside FROZEN 3,714 dataset',
          n_ent_frozen == 0,
          f'{n_ent_frozen} registry rows = {n_ent_frozen_unique} unique '
          f'projects ({n_ent_frozen_unique/len(fr):.1%} of frozen)')

    # how many official 2021-24 rows overall are captured by merged/frozen (year-keyed)
    reg['_in_merged'] = [(int(y), t) in mkeys for y, t in zip(reg['year'], reg['ntitle'])]
    reg['_in_frozen'] = [(int(y), t) in fkeys for y, t in zip(reg['year'], reg['ntitle'])]
    print(f'\nOfficial 2021-24 rows={len(reg)}; year-key matched into merged='
          f'{int(reg["_in_merged"].sum())}; into frozen={int(reg["_in_frozen"].sum())}')
    miss = reg[~reg['_in_frozen']]
    print('Official rows missing from frozen, by year/level/type:')
    print(miss.groupby(['year', 'level', 'type']).size().to_string())

    # ---------- A2: uniqueness ----------
    print('\n--- A2: uniqueness ---')
    check('A2 frozen rows == 3,714', len(fr) == 3714, f'{len(fr)} rows')
    check('A2 project_id unique', fr['project_id'].is_unique,
          f'{fr["project_id"].nunique()} unique ids / {len(fr)} rows')
    # same title in DIFFERENT years = legitimate renewal; only (year,title) dup is an error
    dupkey_f = fr.duplicated(subset=['year', 'ntitle'], keep=False)
    dupkey_m = merged.duplicated(subset=['年份', 'ntitle'], keep=False)
    check('A2 frozen: no duplicated (year, normalized-title) keys',
          dupkey_f.sum() == 0, f'{dupkey_f.sum()} rows')
    check('A2 merged: no duplicated (year, normalized-title) keys',
          dupkey_m.sum() == 0, f'{dupkey_m.sum()} rows')
    cross_yr = merged['ntitle'].value_counts()
    cross_yr = cross_yr[cross_yr > 1]
    print(f'Cross-year same-title renewals (legit, distinct funded projects): '
          f'{len(cross_yr)} titles, {int(merged["ntitle"].isin(cross_yr.index).sum())} rows')

    # ---------- EX: merged 3,887 -> frozen 3,714 ----------
    print('\n--- EX: merged 3,887 -> frozen 3,714 (year-keyed) ---')
    m_not_f = merged[~merged.apply(lambda r: (int(r['年份']), r['ntitle']) in fkeys, axis=1)]
    f_not_m = fr[~fr.apply(lambda r: (int(r['year']), r['ntitle']) in mkeys, axis=1)]
    print(f'merged rows absent from frozen = {len(m_not_f)}; '
          f'frozen rows absent from merged = {len(f_not_m)} '
          f'(reconciles: 3887 - {len(m_not_f)} + {len(f_not_m)} = '
          f'{3887 - len(m_not_f) + len(f_not_m)})')
    if len(f_not_m):
        print('Frozen rows NOT in 五年所有题目:')
        print(f_not_m[['year', 'project_title', 'college', 'level']].to_string(index=False))
    excl_colleges = m_not_f['学院'].value_counts()
    print('Excluded rows by college:')
    print(excl_colleges.to_string())
    check('EX reconciliation 3887 - excl + extra == 3714',
          3887 - len(m_not_f) + len(f_not_m) == 3714,
          f'{3887 - len(m_not_f) + len(f_not_m)}')

    # ---------- A3: funding tiers ----------
    print('\n--- A3: funding tiers ---')
    lvl = fr['level'].value_counts()
    print(lvl.to_string())
    print('By year x level:')
    print(pd.crosstab(fr['year'], fr['level']).to_string())
    # manuscript: university 1,375 (37.0%), provincial 1,657 (44.6%), national 682 (18.4%)
    expected = {'校级': 1375, '省级': 1657, '国家级': 682}
    for k, v in expected.items():
        check(f'A3 {k} == {v}', int(lvl.get(k, 0)) == v, f'observed {int(lvl.get(k, 0))}')
    for k, v in expected.items():
        pct = int(lvl.get(k, 0)) / len(fr) * 100
        print(f'  {k}: {int(lvl.get(k, 0))} ({pct:.1f}%)')

    # official-level counts for 2021-24 (uniqued by title within year)
    print('\nOfficial registries 2021-24 year x level:')
    print(pd.crosstab(reg['year'], reg['level']).to_string())
    print('\nOfficial registries 2021-24 level x type:')
    print(pd.crosstab(reg['level'], reg['type']).to_string())
    print('\nMerged 五年所有题目 year x 获奖等级:')
    print(pd.crosstab(merged['年份'], merged['获奖等级']).to_string())

    # ---------- A4: advisor splitting ----------
    print('\n--- A4: advisor splitting (rebuilt from frozen advisor strings) ---')
    links = set()
    advisor_set = set()
    n_multi = 0
    per_proj = []
    for _, r in fr.iterrows():
        advs = split_advisors(r['advisor'])
        per_proj.append(len(advs))
        if len(advs) > 1:
            n_multi += 1
        for a in advs:
            advisor_set.add(a)
            links.add((r['project_id'], a))
    fr['_nadv'] = per_proj
    check('A4 individual advisors == 1,834', len(advisor_set) == 1834,
          f'{len(advisor_set)}')
    check('A4 advisor-project links == 4,244', len(links) == 4244, f'{len(links)}')
    check('A4 co-supervised projects == 528', n_multi == 528, f'{n_multi}')
    zero_adv = (fr['_nadv'] == 0).sum()
    check('A4 projects with empty advisor field == 0', zero_adv == 0, f'{zero_adv}')

    # ---------- EX2: the 4 "frozen-only" rows — corrupted duplicates? ----------
    print('\n--- EX2: frozen-only rows vs merged (mojibake check) ---')
    from difflib import SequenceMatcher
    for _, r in f_not_m.iterrows():
        y = int(r['year'])
        cand = merged[(merged['年份'] == y) &
                      (merged['学院'].astype(str) == str(r['college']))]
        best = None
        for _, c in cand.iterrows():
            ratio = SequenceMatcher(None, r['ntitle'], c['ntitle']).ratio()
            if best is None or ratio > best[0]:
                best = (ratio, c['项目名称'], c['获奖等级'])
        clean_twin = fr[(fr['year'] == y) &
                        fr['project_title'].apply(lambda t: '?' not in str(t)) &
                        fr['project_title'].apply(
                            lambda t: SequenceMatcher(None, norm_title(t), r['ntitle']).ratio() > 0.9)]
        print(f'frozen: {r["project_title"]} | college={r["college"]} | '
              f'best merged match sim={best[0]:.3f}: {best[1]} [{best[2]}] | '
              f'clean twin in frozen={len(clean_twin) > 0}')

    # ---------- A1b: 2020 keyword screen (no official type field exists) ----------
    print('\n--- A1b: 2020 keyword screen (advisory only; official 2020 type unknown) ---')
    kw = re.compile(r'创业|电商|商业计划|小程序|APP|app|平台|工作室|公司|直播|品牌|加盟|营销|门店|旗舰店')
    d2020 = fr[fr['year'] == 2020]
    hits = d2020[d2020['project_title'].astype(str).str.contains(kw)]
    print(f'2020 projects={len(d2020)}; keyword-flagged (needs manual review)={len(hits)}')
    print(hits[['project_title', 'level', 'college']].to_string(index=False, max_colwidth=40))

    # ---------- A1c: impact of entrepreneurship rows ----------
    print('\n--- A1c: impact of official-typed entrepreneurship rows (2021-24) ---')
    ent_keys = set(zip(ent.loc[ent['_in_frozen'], 'year'].astype(int),
                       ent.loc[ent['_in_frozen'], 'ntitle']))
    fr['is_ent'] = [(int(y), t) in ent_keys for y, t in zip(fr['year'], fr['ntitle'])]
    n_ent = int(fr['is_ent'].sum())
    print(f'Entrepreneurship projects in analytic data: {n_ent} ({n_ent/len(fr)*100:.1f}%)')
    g = fr.groupby('is_ent')['rtas'].agg(['count', 'mean', 'std', 'median'])
    print(g.to_string())
    print('\nMean RTAS by level x is_ent:')
    print(fr.groupby(['level', 'is_ent'])['rtas'].agg(['count', 'mean']).to_string())
    # effect size
    a = fr.loc[fr['is_ent'], 'rtas'].dropna()
    b = fr.loc[~fr['is_ent'], 'rtas'].dropna()
    pooled = np.sqrt(((len(a)-1)*a.var() + (len(b)-1)*b.var()) / (len(a)+len(b)-2))
    print(f"\nCohen d (entrep vs innovation) = {(a.mean()-b.mean())/pooled:.3f}")

    # quick MixedLM sensitivity: exclude entrepreneurship rows
    import statsmodels.formula.api as smf
    fr['is_provincial'] = fr['level'].astype(str).str.contains('省级').astype(int)
    fr['is_national'] = fr['level'].astype(str).str.contains('国家级').astype(int)
    fr['year_centered'] = fr['year'] - 2022
    fr['log_prior3y'] = np.log1p(pd.to_numeric(fr['advisor_prior_3y_works_mean'], errors='coerce'))
    fr['log_sup'] = np.log1p(pd.to_numeric(fr['advisor_prior_supervised_projects'], errors='coerce'))

    def fit(data, label):
        sub = data.dropna(subset=['rtas', 'log_prior3y', 'log_sup', 'is_provincial',
                                  'is_national', 'year_centered', 'college'])
        md = smf.mixedlm('rtas ~ is_provincial + is_national + year_centered '
                         '+ log_prior3y + log_sup', sub, groups=sub['college'])
        res = md.fit(reml=True, method='lbfgs', maxiter=2000)
        vg = float(res.cov_re.iloc[0, 0]); ve = res.scale
        print(f'\n[{label}] n={len(sub)}, colleges={sub["college"].nunique()}, '
              f'ICC={vg/(vg+ve):.4f}')
        for t in ['is_provincial', 'is_national', 'year_centered', 'log_prior3y', 'log_sup']:
            print(f'  {t:18s} beta={res.params[t]:+.5f} p={res.pvalues[t]:.2e}')
        return res
    fit(fr, 'PRIMARY all 3,714')
    fit(fr[~fr['is_ent']], 'EXCLUDE entrepreneurship (2021-24 typed)')

    # ---------- A8: missingness 3,714 -> 3,231 complete cases ----------
    print('\n--- A8: complete-case missingness (3,714 -> model sample) ---')
    covars = ['advisor_prior_3y_works_mean', 'advisor_prior_supervised_projects']
    fr['_cc'] = fr[covars].notna().all(axis=1)
    print(f"complete cases={int(fr['_cc'].sum())}, excluded={int((~fr['_cc']).sum())}")
    print('\nMissingness by year:')
    print(pd.crosstab(fr['year'], fr['_cc'], margins=True).to_string())
    print('\nMissingness by level:')
    print(pd.crosstab(fr['level'], fr['_cc'], margins=True).to_string())
    miss_by_col = fr.groupby('college')['_cc'].agg(['size', 'sum'])
    miss_by_col['excluded'] = miss_by_col['size'] - miss_by_col['sum']
    miss_by_col = miss_by_col[miss_by_col['excluded'] > 0].sort_values('excluded', ascending=False)
    print('\nColleges with most excluded projects:')
    print(miss_by_col.head(12).to_string())
    print('\nRTAS mean: complete vs excluded')
    print(fr.groupby('_cc')['rtas'].agg(['count', 'mean', 'std']).to_string())

    # ---------- summary ----------
    print('\n' + '=' * 70)
    nfail = sum(1 for _, s, _ in results if s == 'FAIL')
    print(f'AUDIT COMPLETE: {len(results)} checks, {nfail} FAIL')
    print('=' * 70)


if __name__ == '__main__':
    main()
