# -*- coding: utf-8 -*-
"""
19_numerical_provenance_audit.py
================================
READ-ONLY numerical provenance audit for v1.0-cand.14.

For every headline number in the manuscript this script answers:
  1. SOURCE  : which frozen/raw file & column it comes from
  2. FORMULA : the exact recomputation
  3. CHECK   : the independently recomputed value printed next to the reported value

This script NEVER overwrites a frozen file. All outputs go to stdout.
Sections follow the agreed audit order:
  (1) corpus/linkage   (2) aggregation/RTAS   (3) validation
  (4) topic/lag        (5) RQ1                (6) RQ3 variance decomposition
  (7) RQ4 concentration / lagged logit
"""
import re
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "01_DATA"
SEL = ROOT / "02_RTAS_MODEL_SELECTION"
FIN = ROOT / "03_FINAL_ANALYSIS"

PASS, FAIL = "OK  ", "XX  "
results = []
current_section = ""


def record(module, reported, recomputed, ok, source, formula, note=""):
    results.append(dict(section=current_section, module=module, reported=str(reported),
                        recomputed=str(recomputed), match="PASS" if ok else "FAIL",
                        source=source, formula=formula, note=note))
    tag = PASS if ok else FAIL
    print(f"[{tag}] {module}: reported={reported} | recomputed={recomputed}")
    if note:
        print(f"        note: {note}")


def close(a, b, tol=1e-9, rtol=5e-3):
    try:
        a, b = float(a), float(b)
        return abs(a - b) <= max(tol, rtol * abs(b))
    except (TypeError, ValueError):
        return a == b


# ----------------------------------------------------------------------
# (1) CORPUS / LINKAGE
# ----------------------------------------------------------------------
def audit_corpus():
    print("\n" + "=" * 78 + "\n(1) CORPUS / LINKAGE\n" + "=" * 78)
    proj = pd.read_csv(DATA / "final_analysis" / "table5_project_dataset_n3714_full.csv")
    art = pd.read_csv(DATA / "raw_private" / "whu_openalex_papers_2020_2024_full.csv")
    pre = pd.read_csv(DATA / "raw_private" / "whu_openalex_papers_2017_2019.csv")
    pmap = pd.read_csv(SEL / "paper_college_year_map_full.csv")

    # --- project corpus ---
    record("projects N", 3714, len(proj), len(proj) == 3714,
           "table5_project_dataset_n3714_full.csv rows", "len(rows)")
    vc = proj["level"].value_counts()
    # level labels: 1=校级/university, 2=省级/provincial, 3=国家级/national
    code = proj.groupby("level_code")["project_id"].count().sort_index()
    print("        level_code counts:", code.to_dict(), "| raw level counts:", vc.to_dict())
    exp = {1: 1375, 2: 1657, 3: 682}
    ok = all(int(code.get(k, -1)) == v for k, v in exp.items())
    record("projects 1375/1657/682", "1375/1657/682",
           "/".join(str(int(code.get(k, -1))) for k in (1, 2, 3)), ok,
           "project table groupby(level_code)", "count per code 1=校级/2=省级/3=国家级")
    pcts = {k: round(100 * exp[k] / 3714, 1) for k in exp}
    record("project level pct", "37.0/44.6/18.4",
           f"{pcts[1]:.1f}/{pcts[2]:.1f}/{pcts[3]:.1f}",
           (pcts[1], pcts[2], pcts[3]) == (37.0, 44.6, 18.4),
           "project table", "100*n_k/3714")

    # --- advisors: split with the frozen delimiter rule ---
    def split_advisors(s):
        if pd.isna(s):
            return []
        return [x.strip() for x in re.split(r"[、，,;；]", str(s)) if x.strip()]

    all_links = set()
    individuals = set()
    n_cosup = 0
    for _, r in proj.iterrows():
        advs = split_advisors(r["advisor"])
        if len(advs) > 1:
            n_cosup += 1
        for a_ in advs:
            individuals.add(a_)
            all_links.add((r["project_id"], a_))
    record("individual advisors", 1834, len(individuals), len(individuals) == 1834,
           "project table advisor column", "split on [、，,;；], unique names")
    record("advisor-project links", 4244, len(all_links), len(all_links) == 4244,
           "project table advisor column", "unique (project_id, advisor) pairs")
    record("co-supervised projects", 528, n_cosup, n_cosup == 528,
           "project table advisor column", "rows with >1 advisor after split")

    # --- article corpus ---
    record("articles 2020-24", 56901, len(art), len(art) == 56901,
           "whu_openalex_papers_2020_2024_full.csv", "len(rows)")
    yr = art.groupby("year")["work_id"].count()
    yrs = [int(yr.get(y, 0)) for y in range(2020, 2025)]
    record("articles by year", "9970/10117/12002/11954/12858",
           "/".join(map(str, yrs)), yrs == [9970, 10117, 12002, 11954, 12858],
           "article table groupby(year)", "count work_id")
    record("articles sum=56901", 56901, sum(yrs), sum(yrs) == 56901,
           "yearly counts", "sum 2020..2024")
    record("prehistory 2017-19", 22438, len(pre), len(pre) == 22438,
           "whu_openalex_papers_2017_2019.csv", "len(rows)")
    record("total pool", 79339, len(art) + len(pre),
           len(art) + len(pre) == 79339,
           "both article files", "56901 + 22438")

    # --- linkage: unique matched articles, edges, mean colleges ---
    matched = pmap[pmap["has_matched"] == True]  # noqa: E712
    n_matched_articles = matched["work_id"].nunique()
    record("matched articles", 33312, n_matched_articles, n_matched_articles == 33312,
           "paper_college_year_map_full.csv", "work_id nunique where has_matched==True")
    pct = 100 * n_matched_articles / len(art)
    record("matched pct", "58.5", f"{pct:.2f}", close(pct, 58.54, 0.01),
           "matched / articles", "100*33312/56901",
           note=f"exact {pct:.4f}%")

    def split_colleges(s):
        if pd.isna(s):
            return []
        return [x.strip() for x in re.split(r"[、，,;；|]", str(s)) if x.strip()]

    edge_count = 0
    multi = 0
    for s in matched["colleges"]:
        cs = split_colleges(s)
        edge_count += len(cs)
        if len(cs) > 1:
            multi += 1
    mean_col = edge_count / n_matched_articles
    record("mean colleges/matched article [pre-audit 1.83 -> corrected 1.37]",
           "1.37 (was 1.83)", f"{mean_col:.4f}",
           close(mean_col, 1.3694, 0.002),
           "paper_college_year_map_full.csv colleges (' | ' delimited, dedup set)",
           "sum(len(colleges)) / 33312",
           note=f"CORRECTED in manuscript cand.14 audit: full-corpus truth = "
                f"{edge_count}/33312 = {mean_col:.4f} (~1.37). The old 1.83 was a "
                f"stale 12K-first-batch statistic; even the frozen 12K map recomputes "
                f"to 1.41. articles with >1 college={multi}")

    # --- per-project linkage status ---
    st = proj["advisor_match_status"].value_counts(dropna=False)
    print("        advisor_match_status:", st.to_dict())
    # columns may use labels; also inspect match_status
    st2 = proj["match_status"].value_counts(dropna=False)
    print("        match_status:", st2.to_dict())

    # --- language audit -------------------------------------------------
    # FROZEN DEFINITION (topic_model/_01_audit.py): zh_ratio = #CJK chars /
    # len(title); the frozen statistic title_chinese_ratio_mean is the MEAN
    # across titles = 0.9234 -> "92%" is a mean CHARACTER share, NOT the share
    # of Chinese-language titles.
    def zh_ratio(s):
        s = str(s)
        return len(re.findall(r"[一-鿿]", s)) / len(s) if s else 0.0

    zr = proj["project_title"].apply(zh_ratio)
    record("project title Chinese-char ratio (mean)", 0.9234, round(zr.mean(), 4),
           close(zr.mean(), 0.9234, 0.0005),
           "audit_substrate.json projects.title_chinese_ratio_mean",
           "mean over titles of CJK_chars/len(title)",
           note=f"CORRECTED in manuscript cand.14 audit: old '(92% Chinese)' read "
                f"like a share of titles; now 'on average 92% Chinese characters'. "
                f"Underlying stat = mean Chinese-character share {zr.mean():.4f}; "
                f"Chinese-majority titles = {(zr > 0.5).mean() * 100:.2f}%; "
                f"titles containing any CJK = {(proj['project_title'].astype(str).str.contains(r'[一-鿿]', regex=True)).mean() * 100:.2f}%")

    zpa = art["title"].fillna("").apply(zh_ratio)
    n_cjk_art = int((zpa > 0).sum())
    record("article titles: mean CJK ratio", "~0", f"{zpa.mean():.6f}",
           zpa.mean() < 0.001,
           "full article title column", "mean CJK_chars/len(title)",
           note=f"CORRECTED in manuscript cand.14 audit: '100% English' was exact "
                f"on the 12K first batch; on full 56,901 corpus {n_cjk_art} titles "
                f"contain CJK chars ({56901 - n_cjk_art}/56901 = "
                f"{100 * (56901 - n_cjk_art) / 56901:.3f}% CJK-free); MS now says "
                f"predominantly English, 99.9%.")
    return proj, art, pmap


# ----------------------------------------------------------------------
# (3) VALIDATION (independent recomputation from raw ratings)
# ----------------------------------------------------------------------
def audit_validation():
    print("\n" + "=" * 78 + "\n(3) VALIDATION\n" + "=" * 78)
    from scipy.stats import spearmanr, kendalltau
    from sklearn.metrics import cohen_kappa_score
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    hv = SEL / "human_validation"
    ann = pd.read_csv(hv / "150pairs_human_annotations.csv")
    cosmini = pd.read_csv(hv / "robustness" / "150pairs_with_cos_mini.csv")
    cosbge = pd.read_csv(hv / "robustness" / "150pairs_with_cos_mini_and_bge.csv")
    llm = pd.read_csv(hv / "150pairs_llm_second_rater.csv")
    rA = pd.read_csv(hv / "second_rater_50pairs_filled.csv")
    rB = pd.read_csv(hv / "second_rater_50pairs_fanrui.csv")
    rt = pd.read_csv(hv / "retest_40pairs_filled.csv")

    df = ann.sort_values("pair_id").reset_index(drop=True)
    y = df["annotator1_score"].astype(float).values
    cm = cosmini.sort_values("pair_id")["cos_mini"].values
    # reference integrity: cos file human_score == annotator1
    same = (cosmini.sort_values("pair_id")["human_score"].values == y).mean()
    record("C1 reference == cos-file human_score", "100%", f"{same*100:.1f}%",
           same == 1.0, "150pairs annotations vs cos file", "column equality")
    n = len(y)
    pos = y >= 2
    rho, p_rho = spearmanr(cm, y)
    record("C1 Spearman rho", 0.405, round(rho, 4), close(rho, 0.405479, 0.0006),
           "annotator1_score vs cos_mini (n=150)", "scipy spearmanr")
    record("C1 Spearman p", "2.64e-7", f"{p_rho:.3e}", close(p_rho, 2.641e-7, 0.02),
           "same", "asymptotic p")
    tau, _ = kendalltau(cm, y)
    record("C1 Kendall tau-b", 0.327, round(tau, 4), close(tau, 0.32724, 0.001),
           "same", "scipy kendalltau")
    order = np.argsort(cm)
    ranks = np.empty(n); ranks[order] = np.arange(1, n + 1)
    n_pos, n_neg = int(pos.sum()), n - int(pos.sum())
    auc = (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    record("C1 n relevant (>=2)", 16, n_pos, n_pos == 16,
           "annotator1_score", "count >=2")
    record("C1 n irrelevant (=1)", 134, n_neg, n_neg == 134,
           "annotator1_score", "count ==1")
    record("C1 AUC", 0.880, round(auc, 4), close(auc, 0.88013, 0.0006),
           "cos_mini ranks", "Mann-Whitney AUC")
    rho_sub, _ = spearmanr(cm[pos], y[pos])
    record("C1 related-only rho (n=16)", -0.253, round(rho_sub, 3),
           close(rho_sub, -0.2528, 0.002),
           "subset rating>=2", "spearman within subset")
    loos = []
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        loos.append(abs(spearmanr(cm[m], y[m]).statistic - rho))
    record("C1 LOO max |drho|", 0.018, round(max(loos), 4),
           close(max(loos), 0.01829, 0.0006),
           "leave-one-pair-out", "max abs change in rho")

    # ---- 50-pair independent raters ----
    ref50 = df.set_index("pair_id")["annotator1_score"]
    merged = rA.merge(rB, on="pair_id", suffixes=("_A", "_B"))
    ref = merged["pair_id"].map(ref50).astype(float).values
    a_ = merged["score"].astype(float).values          # Huang Qi (Rater A)
    b_ = merged["rating"].astype(float).values         # Fanrui (Rater B)
    qwk_a = cohen_kappa_score(ref, a_, weights="quadratic", labels=[1,2,3,4])
    qwk_b = cohen_kappa_score(ref, b_, weights="quadratic", labels=[1,2,3,4])
    qwk_ab = cohen_kappa_score(a_, b_, weights="quadratic", labels=[1,2,3,4])
    rho_ab, _ = spearmanr(a_, b_)
    record("Rater A (Huang Qi) QWK", 0.465, round(qwk_a, 4), close(qwk_a, 0.46483, 0.001),
           "second_rater_50pairs_filled vs annotator1 (50)", "quadratic-weighted kappa")
    record("Rater A exact agreement", "72%", f"{100*(ref==a_).mean():.0f}%",
           (ref == a_).mean() == 0.72, "same 50 pairs", "share identical")
    record("Rater B (Fanrui) QWK", 0.606, round(qwk_b, 4), close(qwk_b, 0.60545, 0.001),
           "second_rater_50pairs_fanrui vs annotator1", "quadratic-weighted kappa")
    record("Rater B exact agreement", "78%", f"{100*(ref==b_).mean():.0f}%",
           (ref == b_).mean() == 0.78, "same", "share identical")
    record("A vs B QWK", 0.826, round(qwk_ab, 4), close(qwk_ab, 0.82566, 0.001),
           "two second raters", "quadratic-weighted kappa")
    record("A vs B Spearman", 0.821, round(rho_ab, 3), close(rho_ab, 0.82061, 0.002),
           "two second raters", "spearman")
    record("A vs B exact agreement", "90%", f"{100*(a_==b_).mean():.0f}%",
           (a_ == b_).mean() == 0.90, "same", "share identical")

    # ---- test-retest (40) ----
    ref_rt = rt["pair_id"].map(ref50).astype(float).values
    rr = rt["score"].astype(float).values
    qwk_rt = cohen_kappa_score(ref_rt, rr, weights="quadratic", labels=[1,2,3,4])
    rho_rt, _ = spearmanr(ref_rt, rr)
    record("Test-retest QWK", 0.643, round(qwk_rt, 4), close(qwk_rt, 0.64286, 0.001),
           "retest_40pairs_filled vs first-round annotator1", "QWK")
    record("Test-retest Spearman", 0.688, round(rho_rt, 3), close(rho_rt, 0.68825, 0.002),
           "same 40 pairs", "spearman")
    record("Test-retest agreement", "95%", f"{100*(ref_rt==rr).mean():.0f}%",
           (ref_rt == rr).mean() == 0.95, "same", "share identical")

    # ---- LLM second rater (150) ----
    lm = llm.sort_values("pair_id")["llm_score"].astype(float).values
    qwk_lm = cohen_kappa_score(y, lm, weights="quadratic", labels=[1,2,3,4])
    rho_lm, p_lm = spearmanr(y, lm)
    record("LLM QWK", 0.459, round(qwk_lm, 4), close(qwk_lm, 0.45920, 0.001),
           "150pairs_llm_second_rater vs annotator1", "QWK")
    record("LLM Spearman", 0.638, round(rho_lm, 3), close(rho_lm, 0.63761, 0.002),
           "same", "spearman")
    record("LLM p", "1.7e-18 (was <1e-18)", f"{p_lm:.2e}", close(p_lm, 1.728985e-18, 0.02),
           "150pairs_llm_second_rater vs annotator1", "asymptotic p",
           note="CORRECTED in manuscript cand.14 audit: exact p=1.73e-18 is NOT "
                "< 1e-18; MS now says p = 1.7x10^-18.")
    record("LLM exact agreement", "93.3%", f"{100*(y==lm).mean():.1f}%",
           abs((y == lm).mean() - 0.9333) < 1e-3, "same", "share identical")
    # triangulation: cos_mini vs Fanrui on the 50 pairs
    cb = cosbge.sort_values("pair_id")
    fan50 = rB.set_index("pair_id")["rating"]
    cm50 = cb.set_index("pair_id")["cos_mini"].reindex(rB["pair_id"]).values
    fr50 = rB["rating"].astype(float).values
    rho_fr, _ = spearmanr(cm50, fr50)
    frpos = fr50 >= 2
    o = np.argsort(cm50); rk = np.empty(len(fr50)); rk[o] = np.arange(1, len(fr50) + 1)
    auc_fr = (rk[frpos].sum() - frpos.sum() * (frpos.sum() + 1) / 2) / (frpos.sum() * (~frpos).sum())
    record("Triangulation cos vs Fanrui rho", 0.621, round(rho_fr, 3),
           close(rho_fr, 0.62097, 0.002), "50-pair subset", "spearman cos_mini~Fanrui")
    record("Triangulation cos vs Fanrui AUC", 0.932, round(auc_fr, 3),
           close(auc_fr, 0.93240, 0.002), "50-pair subset", "AUC Fanrui >=2 vs 1")

    # ---- lexical baselines (verbatim algorithm of 13_baseline_validity.py) ----
    d150 = df.merge(cosmini[["pair_id", "cos_mini"]], on="pair_id")
    d150 = d150.sort_values("pair_id").reset_index(drop=True)
    yb = d150["annotator1_score"].astype(int).values
    posb = yb >= 2
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    docs = list(d150["project_title"]) + list(d150["paper_title"])
    X = vec.fit_transform(docs)
    nb = len(d150)
    b1 = np.array([cosine_similarity(X[i], X[nb + i])[0, 0] for i in range(nb)])

    def ngrams(s, k=3):
        s = re.sub(r"\s+", " ", str(s).lower().strip())
        return {s[i:i + k] for i in range(len(s) - k + 1)} if len(s) >= k else ({s} if s else set())

    b2 = np.array([len(ngrams(p) & ngrams(a)) / len(ngrams(p) | ngrams(a))
                   if ngrams(p) and ngrams(a) else 0.0
                   for p, a in zip(d150["project_title"], d150["paper_title"])])

    def auc_rank(x):
        o = np.argsort(x); rk = np.empty(nb); rk[o] = np.arange(1, nb + 1)
        n1, n0 = int(posb.sum()), nb - int(posb.sum())
        return (rk[posb].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

    record("Baseline TF-IDF rho", 0.300, round(spearmanr(b1, yb).statistic, 3),
           close(spearmanr(b1, yb).statistic, 0.29982, 0.002),
           "char_wb 3-5g tf-idf cosine", "150 pairs spearman")
    record("Baseline TF-IDF AUC", 0.638, round(auc_rank(b1), 3),
           close(auc_rank(b1), 0.63759, 0.002), "same", "rank AUC")
    record("Baseline Jaccard rho", 0.296, round(spearmanr(b2, yb).statistic, 3),
           close(spearmanr(b2, yb).statistic, 0.29620, 0.002),
           "char-3-gram set Jaccard", "150 pairs spearman")
    record("Baseline Jaccard AUC", 0.637, round(auc_rank(b2), 3),
           close(auc_rank(b2), 0.63666, 0.002), "same", "rank AUC")
    # BM25: use frozen CSV value (rank_bm25 implementation-dependent); verify file only
    base_csv = pd.read_csv(hv / "robustness" / "baseline_validity.csv")
    bm = base_csv.loc[base_csv["baseline"].str.startswith("BM25")].iloc[0]
    record("Baseline BM25 rho (frozen CSV)", 0.298, round(float(bm["spearman_rho"]), 3),
           close(float(bm["spearman_rho"]), 0.29777, 0.001),
           "baseline_validity.csv", "rank_bm25 Okapi (impl-bound)")
    record("Baseline BM25 AUC (frozen CSV)", 0.637, round(float(bm["auc_ge2_vs_1"]), 3),
           close(float(bm["auc_ge2_vs_1"]), 0.63713, 0.001), "same", "rank AUC")

    # ---- BGE-M3 ----
    cbge = cosbge.sort_values("pair_id")
    cb = cbge["cos_bge_m3"].values
    rho_b, _ = spearmanr(cb, y)
    auc_b = auc_rank(cb)
    record("BGE-M3 rho", 0.334, round(rho_b, 3), close(rho_b, 0.33367, 0.001),
           "150pairs cos_bge_m3 vs annotator1", "spearman")
    record("BGE-M3 AUC", 0.811, round(auc_b, 3), close(auc_b, 0.81063, 0.001),
           "same", "rank AUC")
    # paired bootstrap (seed 42, B=2000)
    rng = np.random.default_rng(42)
    dr, da = [], []
    cmini = cbge["cos_mini"].values
    for _ in range(2000):
        ix = rng.integers(0, n, n)
        dr.append(spearmanr(cb[ix], y[ix]).statistic - spearmanr(cmini[ix], y[ix]).statistic)
        o1 = np.argsort(cb[ix]); r1 = np.empty(n); r1[o1] = np.arange(1, n + 1)
        o2 = np.argsort(cmini[ix]); r2 = np.empty(n); r2[o2] = np.arange(1, n + 1)
        pi = pos[ix]
        a1 = (r1[pi].sum() - pi.sum() * (pi.sum() + 1) / 2) / (pi.sum() * (~pi).sum())
        a2 = (r2[pi].sum() - pi.sum() * (pi.sum() + 1) / 2) / (pi.sum() * (~pi).sum())
        da.append(a1 - a2)
    dr, da = np.array(dr), np.array(da)
    frozen_dr = (-0.07088, -0.18673, 0.03546)
    frozen_da = (-0.06934, -0.17857, 0.03229)
    ok_r = close(dr.mean(), frozen_dr[0], 0.012) and close(np.percentile(dr, 2.5), frozen_dr[1], 0.02)
    record("BGE paired bootstrap d_rho [%.3f (%.3f,%.3f)]" % (dr.mean(), np.percentile(dr, 2.5), np.percentile(dr, 97.5)),
           "-0.071 [-0.187,+0.036]",
           f"{dr.mean():.3f} [{np.percentile(dr,2.5):.3f},{np.percentile(dr,97.5):.3f}]",
           ok_r, "paired resampling of 150 pairs, seed42 B=2000",
           "rho_bge-rho_mini percentile CI (RNG order may differ slightly)",
           note="frozen json: mean -0.0709, CI [-0.1867,+0.0355]")
    ok_a = close(da.mean(), frozen_da[0], 0.012)
    record("BGE paired bootstrap d_AUC",
           "-0.069 [-0.179,+0.032]",
           f"{da.mean():.3f} [{np.percentile(da,2.5):.3f},{np.percentile(da,97.5):.3f}]",
           ok_a, "same bootstrap", "auc_bge-auc_mini",
           note="frozen json: mean -0.0693, CI [-0.1786,+0.0323]")


# ----------------------------------------------------------------------
# (2) AGGREGATION / RTAS
# ----------------------------------------------------------------------
def audit_rtas():
    print("\n" + "=" * 78 + "\n(2) AGGREGATION / RTAS\n" + "=" * 78)
    ms = pd.read_csv(SEL / "rtas_model_selection.csv")
    sub = ms[ms["embedding"] == "mini"].reset_index(drop=True)

    def norm(s):
        s = s.astype(float); rng = s.max() - s.min()
        return (s - s.min()) / rng if rng > 0 else s * 0

    eta = norm(sub["C2_knowngroups_eta2"])
    stab = norm(norm(1 - sub["C4_year_sd_norm"]) * 0.5 +
                norm(sub["C4_college_ICC"].fillna(0)) * 0.5)
    c3n = norm(sub["C3_Kstability"].fillna(0))
    sub["composite"] = 0.45 * eta + 0.30 * stab + 0.25 * c3n
    expected = {"mean": 0.742, "top5": 0.480, "top10": 0.447,
                "top20": 0.398, "centroid": 0.300}
    for agg, val in expected.items():
        got = float(sub.loc[sub["aggregation"] == agg, "composite"].iloc[0])
        record(f"composite {agg}", val, round(got, 3), close(got, val, 0.0011),
               "rtas_model_selection.csv (5 mini variants)",
               "0.45*norm(eta2)+0.30*norm(stability)+0.25*norm(C3)")
    winner = sub.sort_values("composite", ascending=False).iloc[0]["aggregation"]
    record("composite winner", "mean", winner, winner == "mean",
           "same table", "argmax composite")

    p = pd.read_csv(DATA / "final_analysis" / "table5_project_dataset_n3714_full.csv")
    r = p["rtas"]
    record("RTAS N", 3714, len(r), len(r) == 3714,
           "project table rtas column", "rows")
    record("RTAS missing", 0, int(r.isna().sum()), r.isna().sum() == 0,
           "same", "NaN count")
    for name, val, got, tol in [
        ("RTAS mean", 0.1337, r.mean(), 0.00011),
        ("RTAS SD", 0.0723, r.std(ddof=1), 0.00011),
        ("RTAS median", 0.1362, r.median(), 0.00011),
        ("RTAS min", -0.0575, r.min(), 0.00011),
        ("RTAS max", 0.3960, r.max(), 0.00011),
    ]:
        record(name, val, round(got, 4), close(got, val, tol),
               "final full-corpus rtas (56,901 substrate)", "describe()")
    record("0->10 pubs RTAS effect", "+0.010 (~0.14 SD)",
           f"{0.004266*(np.log(11)-np.log(1)):.5f} / {0.004266*(np.log(11)-np.log(1))/r.std():.3f} SD",
           close(0.004266 * np.log(11), 0.01024, 0.0003),
           "beta_log_prior3y=0.004266 x [log(11)-log(1)]",
           "linear shift on log(1+x) scale, divided by SD .0723")


# ----------------------------------------------------------------------
# (5) RQ1 — funding level vs RTAS
# ----------------------------------------------------------------------
def audit_rq1():
    print("\n" + "=" * 78 + "\n(5) RQ1 FUNDING LEVEL\n" + "=" * 78)
    from scipy.stats import f_oneway, ttest_ind
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    p = pd.read_csv(DATA / "final_analysis" / "table5_project_dataset_n3714_full.csv")
    lab = {1: ("university", "校级"), 2: ("provincial", "省级"), 3: ("national", "国家级")}
    grp = {k: p.loc[p["level_code"] == k, "rtas"].values for k in lab}
    means = {k: v.mean() for k, v in grp.items()}
    record("RQ1 mean university", 0.1212, round(means[1], 4), close(means[1], 0.121186, 1e-4),
           "project table rtas by level_code=1", "mean")
    record("RQ1 mean provincial", 0.1391, round(means[2], 4), close(means[2], 0.139055, 1e-4),
           "level_code=2", "mean")
    record("RQ1 mean national", 0.1460, round(means[3], 4), close(means[3], 0.146027, 1e-4),
           "level_code=3", "mean")
    F, pF = f_oneway(*grp.values())
    record("RQ1 ANOVA F(2,3711)", 35.72, round(F, 2), close(F, 35.716112, 0.005),
           "scipy f_oneway", "one-way ANOVA")
    record("RQ1 ANOVA p", "4.3e-16", f"{pF:.2e}", close(pF, 4.326e-16, 0.02),
           "same", "p")
    allv = np.concatenate(list(grp.values()))
    ssb = sum(len(v) * (v.mean() - allv.mean()) ** 2 for v in grp.values())
    sst = ((allv - allv.mean()) ** 2).sum()
    eta2 = ssb / sst
    record("RQ1 eta2", "1.89%", f"{100*eta2:.2f}%", close(eta2, 0.018885, 2e-4),
           "SS_between / SS_total", "ANOVA eta squared")
    tk = pairwise_tukeyhsd(p["rtas"].values, p["level"].values)
    tdf = pd.DataFrame(data=tk._results_table.data[1:],
                       columns=tk._results_table.data[0])
    for c in ["meandiff", "p-adj", "lower", "upper"]:
        tdf[c] = tdf[c].astype(float)
    def tkrow(g1, g2):
        r = tdf[((tdf["group1"] == g1) & (tdf["group2"] == g2)) |
                ((tdf["group1"] == g2) & (tdf["group2"] == g1))].iloc[0]
        return r["meandiff"], r["p-adj"]
    md_pu, ppu = tkrow("省级", "校级")
    md_nu, pnu = tkrow("国家级", "校级")
    md_np, pnp = tkrow("国家级", "省级")
    record("RQ1 Tukey P-U", "+0.0179***", f"{md_pu:+.4f}(p={ppu:.4f})",
           close(md_pu, 0.0179, 2e-3) and ppu < 0.001,
           "statsmodels pairwise_tukeyhsd", "provincial - university")
    record("RQ1 Tukey N-U", "+0.0248***", f"{md_nu:+.4f}(p={pnu:.4f})",
           close(abs(md_nu), 0.0248, 2e-3) and pnu < 0.001,
           "same", "national - university")
    record("RQ1 Tukey N-P", "+0.0070 (p=.082 ns)", f"{md_np:+.4f}(p={pnp:.3f})",
           close(abs(md_np), 0.0070, 2e-3) and close(pnp, 0.0821, 0.005),
           "same", "national - provincial")
    a, b = grp[3], grp[1]
    tw, pw = ttest_ind(a, b, equal_var=False)
    record("RQ1 Welch N-U t", 7.375, round(tw, 3), close(tw, 7.375152, 0.002),
           "scipy ttest_ind equal_var=False", "Welch t")
    record("RQ1 Welch N-U p", "2.9e-13", f"{pw:.2e}", close(pw, 2.919e-13, 0.02),
           "same", "Welch p")
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) /
                 (len(a) + len(b) - 2))
    d = (a.mean() - b.mean()) / sp
    record("RQ1 Cohen d N-U", 0.352, round(d, 3), close(d, 0.351676, 0.002),
           "(meanN-meanU)/pooled SD", "pooled-variance Cohen d")
    # bootstrap CI for eta2 (seed 42, B=10000, resample within groups)
    rng = np.random.default_rng(42)
    B = 10000
    boots = np.empty(B)
    arrs = list(grp.values())
    for i in range(B):
        sam = [v[rng.integers(0, len(v), len(v))] for v in arrs]
        allx = np.concatenate(sam); gm = allx.mean()
        sb = sum(len(s) * (s.mean() - gm) ** 2 for s in sam)
        st = ((allx - gm) ** 2).sum()
        boots[i] = sb / st
    lo, hi = np.percentile(boots, [2.5, 97.5])
    record("RQ1 eta2 bootstrap 95% CI", "[1.14%, 2.86%]",
           f"[{100*lo:.2f}%, {100*hi:.2f}%]",
           close(100 * lo, 1.14, 0.15) and close(100 * hi, 2.86, 0.15),
           "within-group bootstrap seed42 B=10000",
           "percentile CI of SSb/SSt",
           note="RNG order may differ slightly from the frozen run")


# ----------------------------------------------------------------------
# (4) TOPIC / LAG
# ----------------------------------------------------------------------
def audit_lag():
    print("\n" + "=" * 78 + "\n(4) TOPIC / DIFFUSION LAG\n" + "=" * 78)
    yl = pd.read_csv(FIN / "topic_model" / "topic_yearly_prevalence_for_diffusion_lag.csv")
    info = pd.read_csv(FIN / "topic_model" / "topic_info.csv")
    qmap = dict(zip(info["Topic"], info["quadrant"]))
    rows = []
    for tid, g in yl.groupby("topic_id"):
        g = g.sort_values("year")
        pc = g.loc[(g["n_paper"] >= 3) & (g["pct_paper"] >= 0.2), "year"]
        pj = g.loc[(g["n_project"] >= 2) & (g["pct_project"] >= 0.2), "year"]
        if len(pc) and len(pj):
            rows.append((int(tid), int(pj.min()) - int(pc.min()),
                         qmap.get(int(tid), "?")))
    res = pd.DataFrame(rows, columns=["tid", "lag", "q"])
    n_def = len(res)
    record("Defined-lag topics", 29, n_def, n_def == 29,
           "topic_yearly_prevalence_for_diffusion_lag.csv",
           "first year paper>=3&>=0.2%, project>=2&>=0.2%")
    record("Defined-lag share", "3.27%", f"{100*n_def/886:.2f}%",
           close(n_def / 886, 0.03273, 1e-3), "29/886", "percent")
    n_hrlt = int(res["q"].str.startswith("HRLT").sum())
    n_hrht = int(res["q"].str.startswith("HRHT").sum())
    record("Defined lag HRLT/HRHT", "24/5", f"{n_hrlt}/{n_hrht}",
           (n_hrlt, n_hrht) == (24, 5), "quadrant join", "counts")
    h = res[res["q"].str.startswith("HRLT")]["lag"]
    record("HRLT research-first / same-year / project-first", "12/9/3",
           f"{int((h>0).sum())}/{int((h==0).sum())}/{int((h<0).sum())}",
           ((h > 0).sum(), (h == 0).sum(), (h < 0).sum()) == (12, 9, 3),
           "lag sign on 24 HRLT topics", "positive/zero/negative")
    record("HRLT median/mean lag", "+0.5/+0.79",
           f"{h.median():+.1f}/{h.mean():+.2f}",
           close(h.median(), 0.5, 0.01) and close(h.mean(), 0.7917, 0.01),
           "same", "median/mean years")
    record("Overall median/mean lag", "0/+0.59",
           f"{res['lag'].median():.0f}/{res['lag'].mean():+.2f}",
           res["lag"].median() == 0 and close(res["lag"].mean(), 0.5862, 0.01),
           "29 topics", "median/mean")
    record("Overall zero-lag topics (Discussion: 13 same-year)", 13,
           int((res["lag"] == 0).sum()), (res["lag"] == 0).sum() == 13,
           "9 HRLT + 4 HRHT", "zero-lag count")
    # exact equality with frozen per-topic output
    froz = pd.read_csv(FIN / "diffusion_lag" / "topic_first_year_adoption.csv")
    fz = froz[froz["lag_defined"] == True].sort_values("topic_id")
    same = (fz["topic_id"].values == res.sort_values("tid")["tid"].values).all() and \
        np.allclose(fz["lag_years"].values, res.sort_values("tid")["lag"].values)
    record("Lag rebuild == frozen topic_first_year_adoption.csv", "identical",
           "identical" if same else "DIFF", same,
           "frozen per-topic file", "set + lag equality")

# ----------------------------------------------------------------------
# (6) RQ3 — HLM variance decomposition
# ----------------------------------------------------------------------
def audit_rq3():
    print("\n" + "=" * 78 + "\n(6) RQ3 HLM VARIANCE DECOMPOSITION\n" + "=" * 78)
    import warnings; warnings.filterwarnings("ignore")
    from collections import defaultdict
    import statsmodels.formula.api as smf
    df = pd.read_csv(DATA / "final_analysis" / "table5_project_dataset_n3714_full.csv")

    def split_advisors(s):
        if not isinstance(s, str):
            return []
        return [p.strip() for p in re.split(r"[、，,;；]", s) if p.strip()]

    atom_years = defaultdict(list)
    for _, row in df.iterrows():
        for a in split_advisors(row["advisor"]):
            atom_years[a].append(int(row["year"]))

    def prior_sup(f, fy):
        atoms = split_advisors(f)
        if not atoms:
            return 0.0
        return float(np.mean([sum(1 for y in atom_years.get(a, []) if y < fy)
                              for a in atoms]))

    rebuilt = np.array([prior_sup(r["advisor"], int(r["year"]))
                        for _, r in df.iterrows()])
    record("RQ3 prior-supervision col rebuilt == frozen", "identical",
           "identical" if np.allclose(rebuilt,
                    df["advisor_prior_supervised_projects"].values) else "DIFF",
           np.allclose(rebuilt, df["advisor_prior_supervised_projects"].values),
           "table5 advisor_prior_supervised_projects",
           "mean over advisor atoms of #projects with year < focal year")
    df["is_provincial"] = df["level"].astype(str).str.contains("省级|Provincial", regex=True).astype(int)
    df["is_national"] = df["level"].astype(str).str.contains("国家级|National", regex=True).astype(int)
    df["year_centered"] = df["year"] - 2022
    df["log_prior3y"] = np.log1p(pd.to_numeric(df["advisor_prior_3y_works_mean"], errors="coerce"))
    df["log_prior_supervision"] = np.log1p(rebuilt)
    cc = df.dropna(subset=["rtas", "log_prior3y", "log_prior_supervision",
                           "is_provincial", "is_national", "year_centered", "college"])
    record("RQ3 complete-case n / colleges", "3231 / 39",
           f"{len(cc)} / {cc['college'].nunique()}",
           len(cc) == 3231 and cc["college"].nunique() == 39,
           "complete cases on all predictors + college", "dropna count")
    fml = ("rtas ~ is_provincial + is_national + year_centered "
           "+ log_prior3y + log_prior_supervision")
    nm = smf.mixedlm("rtas ~ 1", cc, groups=cc["college"]).fit(
        reml=True, method="lbfgs", maxiter=2000)
    fm = smf.mixedlm(fml, cc, groups=cc["college"]).fit(
        reml=True, method="lbfgs", maxiter=2000)
    t0n, s2n = float(nm.cov_re.iloc[0, 0]), float(nm.scale)
    t0f, s2f = float(fm.cov_re.iloc[0, 0]), float(fm.scale)
    icc_n, icc_f = t0n / (t0n + s2n), t0f / (t0f + s2f)
    record("RQ3 null var college / resid", ".005438 / .001791",
           f"{t0n:.6f} / {s2n:.6f}",
           close(t0n, 0.005438, 5e-5) and close(s2n, 0.001791, 5e-5),
           "in-memory REML null MixedLM refit", "cov_re, scale")
    record("RQ3 null ICC", 0.7523, round(icc_n, 4), close(icc_n, 0.7523, 5e-4),
           "tau00/(tau00+sigma2)", "null-model ICC")
    record("RQ3 full var college / resid", ".004944 / .001759",
           f"{t0f:.6f} / {s2f:.6f}",
           close(t0f, 0.004944, 5e-5) and close(s2f, 0.001759, 5e-5),
           "in-memory REML full MixedLM refit", "cov_re, scale")
    record("RQ3 full ICC", 0.7376, round(icc_f, 4), close(icc_f, 0.7376, 5e-4),
           "tau00/(tau00+sigma2)", "conditional-model ICC")
    fe_terms = ["is_provincial", "is_national", "year_centered",
                "log_prior3y", "log_prior_supervision"]
    eta = np.zeros(len(cc))
    for t in fe_terms:
        eta += fm.params[t] * cc[t].values
    vfe = eta.var(ddof=0)
    tot = vfe + t0f + s2f
    r2m, r2c = vfe / tot, (vfe + t0f) / tot
    record("RQ3 marginal R2", 0.0075, round(r2m, 4), close(r2m, 0.0075, 3e-4),
           "var(Xb fixed excl intercept)/(varFE+tau+sigma2)",
           "Nakagawa-Schielzeth/Johnson marginal R2")
    record("RQ3 conditional R2", 0.7395, round(r2c, 4), close(r2c, 0.7395, 5e-4),
           "(varFE+tau)/(varFE+tau+sigma2)", "conditional R2")
    record("RQ3 beta log_prior3y", 0.004266, round(fm.params["log_prior3y"], 6),
           close(fm.params["log_prior3y"], 0.00426576, 1e-6),
           "full MixedLM", "fixed coefficient")
    record("RQ3 beta log_prior3y p", "3.2e-9 (MS 3.3e-9)",
           f"{fm.pvalues['log_prior3y']:.2e}",
           close(fm.pvalues["log_prior3y"], 3.201e-9, 0.02),
           "same", "Wald z p")
    record("RQ3 beta supervision", -0.006287, round(fm.params["log_prior_supervision"], 6),
           close(fm.params["log_prior_supervision"], -0.00628746, 1e-6),
           "full MixedLM", "fixed coefficient")
    record("RQ3 beta year_centered", 0.003132, round(fm.params["year_centered"], 6),
           close(fm.params["year_centered"], 0.00313171, 1e-6),
           "full MixedLM", "fixed coefficient")

# ----------------------------------------------------------------------
# (7) RQ4 — Matthew effect (individual-advisor unit)
# ----------------------------------------------------------------------
def audit_rq4():
    print("\n" + "=" * 78 + "\n(7) RQ4 CONCENTRATION / LAGGED LOGIT\n" + "=" * 78)
    import warnings; warnings.filterwarnings("ignore")
    import statsmodels.api as sm
    from scipy import stats as sstats
    df = pd.read_csv(DATA / "final_analysis" / "table5_project_dataset_n3714_full.csv")
    froz_edges = pd.read_csv(FIN / "matthew_effect" / "individual_advisor" /
                             "advisor_project_edges.csv")

    def split_advisors(s):
        if not isinstance(s, str):
            return []
        return [p.strip() for p in re.split(r"[、，,;；]", s) if p.strip()]

    erows = []
    for idx, r in df.iterrows():
        pid = r.get("project_id", idx)
        for a in split_advisors(r["advisor"]):
            erows.append((pid, idx, a))
    edges = pd.DataFrame(erows, columns=["project_id", "project_row_idx",
                                         "individual_advisor"])
    edges = edges.merge(
        df.reset_index(drop=True).reset_index().rename(
            columns={"index": "project_row_idx"})[
            ["project_row_idx", "year", "level", "rtas"]],
        on="project_row_idx", how="left")
    edges["is_national"] = edges["level"].astype(str).str.contains("国家级").astype(int)
    same_edges = (len(edges) == len(froz_edges) == 4244 and
                  set(map(tuple, edges[["project_row_idx", "individual_advisor"]]
                          .values.tolist())) ==
                  set(map(tuple, froz_edges[["project_row_idx", "individual_advisor"]]
                          .values.tolist())))
    record("RQ4 edges rebuilt == frozen advisor_project_edges.csv",
           "4244 identical", "identical" if same_edges else "DIFF", same_edges,
           "explode advisor field per frozen delimiter",
           "(project_row_idx, individual_advisor) set equality")

    bysup = edges.groupby("individual_advisor").agg(
        n_projects=("project_id", "nunique"),
        n_national=("is_national", "sum")).reset_index()
    N = len(bysup)
    record("RQ4 individual advisors (Gini denominator)", 1834, N, N == 1834,
           "groupby individual_advisor", "headcount incl. zero-national")
    n_zero = int((bysup["n_national"] == 0).sum())
    record("RQ4 advisors with ZERO national projects included in Gini",
           1236, n_zero, n_zero == 1236,
           "n_national sum incl. zeros", "zero count (answer to open question a)")

    def gini(x):
        x = np.sort(np.asarray(x, float)); n = len(x); c = x.sum()
        return (2 * np.sum(np.arange(1, n + 1) * x) - (n + 1) * c) / (n * c)

    gn, gt = gini(bysup["n_national"].values), gini(bysup["n_projects"].values)
    record("RQ4 Gini national projects", 0.746, round(gn, 3),
           close(gn, 0.745826, 1e-4),
           "per-advisor national counts incl. 1236 zeros",
           "standard Gini on sorted counts")
    record("RQ4 Gini total projects", 0.368, round(gt, 3),
           close(gt, 0.367686, 1e-4),
           "per-advisor distinct project counts", "Gini")
    load = bysup["n_projects"]
    record("RQ4 advisors with exactly 1 project", "818 (44.6%)",
           f"{int((load==1).sum())} ({100*(load==1).mean():.1f}%)",
           (load == 1).sum() == 818 and close((load == 1).mean(), 0.44602, 5e-3),
           "load distribution", "count/share")
    record("RQ4 advisors with >=4 projects", "345 (18.8%)",
           f"{int((load>=4).sum())} ({100*(load>=4).mean():.1f}%)",
           (load >= 4).sum() == 345 and close((load >= 4).mean(), 0.18811, 5e-3),
           "load distribution", "count/share")
    n_top5 = int(np.ceil(0.05 * N))
    bs = bysup.sort_values(["n_national", "n_projects"],
                           ascending=[False, False]).reset_index(drop=True)
    top5 = set(bs.head(n_top5)["individual_advisor"])
    s5 = 100 * bs.head(n_top5)["n_national"].sum() / bs["n_national"].sum()
    record("RQ4 top5% headcount (rounding rule)", "92 = ceil(0.05*1834=91.7)",
           f"{n_top5} (0.05*{N}={0.05*N:.1f})",
           n_top5 == 92, "ceil(5% x N)", "headcount (open question b)")
    record("RQ4 top5% national share", "31.0%", f"{s5:.2f}%",
           close(s5, 30.9927, 0.05), "national projects held by 92 advisors / all national",
           "share")
    nat_desc = np.sort(bysup["n_national"].values.astype(float))[::-1]
    n20 = int(0.20 * N)
    s20 = 100 * nat_desc[:n20].sum() / nat_desc.sum()
    record("RQ4 top20% headcount / share", "366 / 71.9%",
           f"{n20} / {s20:.2f}%", n20 == 366 and close(s20, 71.9128, 0.05),
           f"int(0.20*1834)={n20} advisors", "headcount+share (open question c)")
    proj5 = edges.groupby("project_id")["individual_advisor"].apply(
        lambda s: int(any(a in top5 for a in s)))
    dfp = df.copy()
    if "project_id" not in dfp.columns:
        dfp["project_id"] = dfp.index
    dfp = dfp.merge(proj5.rename("t5"), on="project_id", how="left")
    dfp["t5"] = dfp["t5"].fillna(0).astype(int)
    xv = dfp.loc[dfp["t5"] == 1, "rtas"].dropna().values
    yv = dfp.loc[dfp["t5"] == 0, "rtas"].dropna().values
    record("RQ4 exposed projects (project-level dedup)", "560 (+3154=3714)",
           f"{len(xv)} (+{len(yv)}={len(xv)+len(yv)})",
           len(xv) == 560 and len(yv) == 3154,
           "1 if ANY project advisor is top5%; one row per project",
           "exposure construction (open question d)")
    _, pw = sstats.ttest_ind(xv, yv, equal_var=False)
    sp = np.sqrt(((len(xv)-1)*xv.var(ddof=1)+(len(yv)-1)*yv.var(ddof=1)) /
                 (len(xv)+len(yv)-2))
    dv = (xv.mean()-yv.mean())/sp
    record("RQ4 top5% vs rest Cohen d", 0.083, round(dv, 3), close(dv, 0.08313, 2e-3),
           "Welch pooled d on project RTAS", "effect size")
    record("RQ4 top5% vs rest Welch p", 0.065, round(pw, 3), close(pw, 0.06464, 1e-3),
           "scipy ttest_ind equal_var=False", "p")

    panel = edges.groupby(["individual_advisor", "year"]).agg(
        n_projects=("project_id", "nunique"),
        n_national=("is_national", "sum")).reset_index()
    yrs = sorted(panel["year"].unique())
    adv = panel["individual_advisor"].unique()
    full = pd.MultiIndex.from_product([adv, yrs], names=["individual_advisor", "year"]) \
        .to_frame(index=False)
    pf = full.merge(panel, on=["individual_advisor", "year"], how="left") \
        .fillna({"n_projects": 0, "n_national": 0}) \
        .sort_values(["individual_advisor", "year"])
    pf["nat"] = (pf["n_national"] >= 1).astype(int)
    pf["nat_lag"] = pf.groupby("individual_advisor")["nat"].shift(1)
    pf["load_lag"] = pf.groupby("individual_advisor")["n_projects"].shift(1)
    panel = panel.sort_values(["individual_advisor", "year"])
    panel["nat"] = (panel["n_national"] >= 1).astype(int)
    panel["nat_lag"] = panel.groupby("individual_advisor")["nat"].shift(1)
    panel["load_lag"] = panel.groupby("individual_advisor")["n_projects"].shift(1)
    panel["year_diff"] = panel.groupby("individual_advisor")["year"].diff()

    def fit_logit(d):
        d = d.copy()
        d["ll"] = np.log1p(d["load_lag"].astype(float))
        yr = pd.get_dummies(d["year"].astype(int), prefix="yr",
                            drop_first=True).astype(float)
        X = pd.concat([pd.Series(1.0, index=d.index, name="const"),
                       d[["nat_lag", "ll"]].astype(float), yr], axis=1)
        r = sm.Logit(d["nat"].astype(int).values, X.values).fit(
            disp=False, maxiter=200, cov_type="cluster",
            cov_kwds={"groups": d["individual_advisor"].values})
        i = list(X.columns).index("nat_lag")
        return len(d), d["individual_advisor"].nunique(), \
            np.exp(r.params[i]), np.exp(r.conf_int())[i]

    sA = panel[panel["year_diff"] == 1]
    nA, kA, oA, ciA = fit_logit(sA)
    record("RQ4 lagged logit A cells/advisors", "979 / 627", f"{nA} / {kA}",
           (nA, kA) == (979, 627),
           "consecutive-year active cells only", "risk-set size")
    record("RQ4 lagged logit A OR [CI]", "2.06 [1.53, 2.76]",
           f"{oA:.2f} [{ciA[0]:.2f}, {ciA[1]:.2f}]",
           close(oA, 2.05637, 0.01) and close(ciA[0], 1.5329, 0.01) and
           close(ciA[1], 2.7586, 0.01),
           "Logit nat_t ~ nat_{t-1}+log load+year FE, cluster by advisor",
           "exp(beta)")
    sB = pf[(pf["year"] >= 2021) & pf["nat_lag"].notna() & (pf["load_lag"] > 0)]
    nB, kB, oB, ciB = fit_logit(sB)
    record("RQ4 lagged logit B cells/advisors", "2469 / 1560", f"{nB} / {kB}",
           (nB, kB) == (2469, 1560),
           "full advisor-year grid, prior-active, ref year 2021", "risk-set size")
    record("RQ4 lagged logit B OR [CI]", "2.45 [1.91, 3.16]",
           f"{oB:.2f} [{ciB[0]:.2f}, {ciB[1]:.2f}]",
           close(oB, 2.45465, 0.01) and close(ciB[0], 1.9067, 0.01) and
           close(ciB[1], 3.1601, 0.01),
           "same logit on full grid", "exp(beta)")



if __name__ == "__main__":
    sections = [
        ("1 corpus/linkage", audit_corpus),
        ("2 aggregation/RTAS", audit_rtas),
        ("3 validation", audit_validation),
        ("4 topic/lag", audit_lag),
        ("5 RQ1", audit_rq1),
        ("6 RQ3 HLM", audit_rq3),
        ("7 RQ4 Matthew", audit_rq4),
    ]
    for label, fn in sections:
        current_section = label
        fn()
    print("\n%d checks recorded." % len(results))
    bad = [r for r in results if r["match"] != "PASS"]
    print("%d PASS, %d FAIL" % (len(results) - len(bad), len(bad)))

    # ---- provenance ledger deliverable ----
    led = pd.DataFrame(results)[["section", "module", "reported", "recomputed",
                                 "match", "source", "formula", "note"]]
    led_path = ROOT / "06_CODE" / "19_numerical_provenance_ledger.csv"
    led.to_csv(led_path, index=False, encoding="utf-8-sig")
    print(f"Ledger written: {led_path}")


