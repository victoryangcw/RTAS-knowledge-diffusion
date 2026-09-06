# -*- coding: utf-8 -*-
"""12_llm_second_rater.py — v1.0-cand.9 (SECONDARY/ROBUSTNESS, not part of the frozen chain)

LLM-as-second-rater for the 150-pair validation set: fills the annotator2 slot
that was pre-registered in the annotation file design but never executed.

Design
  - Blind: the model sees ONLY project_title + paper_title (no human score,
    no cosine similarity, no citation counts, no college/level metadata).
  - Deterministic: temperature = 0, JSON response format, fixed prompt v1
    (prompt text mirrored verbatim in RATING_RUBRIC.md).
  - Model: gpt-4o (API key from env OPENAI_API_KEY or 06_CODE/.openai_key file).
  - Checkpoint every 25 pairs; idempotent (re-run resumes from saved scores).

Outputs (new files only):
  02_RTAS_MODEL_SELECTION/human_validation/150pairs_llm_second_rater.csv
      pair_id, llm_score, llm_rationale, model, prompt_version
  Console + 02_RTAS_MODEL_SELECTION/human_validation/robustness/llm_agreement_stats.csv
      human-LLM agreement (quadratic-weighted kappa, Spearman, exact %),
      and RTAS-LLM triangulation Spearman (vs frozen RTAS-human +0.405).
"""
import json, os, re, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

SEED_MARKER = '42'  # documentation only; no sampling in this script
PROJ = Path(r'D:/vc-task/RTAS_FINAL_PROJECT')
HV = PROJ / '02_RTAS_MODEL_SELECTION' / 'human_validation'
SRC_ANN = Path(r'D:/dachuang_outputs/SCI_最终投稿图表包/mytask/标注任务_150对_人工LLM混合_已标注.csv')
COS_CSV = HV / 'robustness' / '150pairs_with_cos_mini.csv'
OUT_CSV = HV / '150pairs_llm_second_rater.csv'
AGG_CSV = HV / 'robustness' / 'llm_agreement_stats.csv'

MODEL = 'gpt-4o'
TEMPERATURE = 0.0
PROMPT_VERSION = 'v1'

SYSTEM_PROMPT = (
    'You are an expert rater in a bibliometric validation study. '
    'Rate the SEMANTIC RELEVANCE of a scientific paper (given by its title) '
    'to an undergraduate research project (given by its title), using ONLY '
    'the information contained in the two titles.\n\n'
    'Rubric:\n'
    '4 = Directly relevant: same research problem, or directly supporting method/data.\n'
    '3 = Substantially relevant: same problem area or same methodology domain, clear overlap.\n'
    '2 = Weakly relevant: shares a broad discipline or generic methods, but different problems.\n'
    '1 = Not relevant: no meaningful semantic connection.\n\n'
    'Respond ONLY with a JSON object: {"score": <integer 1-4>, "rationale": "<one short sentence>"}'
)


def load_key():
    k = os.environ.get('OPENAI_API_KEY', '').strip()
    if k:
        return k, 'env OPENAI_API_KEY'
    kf = PROJ / '06_CODE' / '.openai_key'
    if kf.exists():
        k = kf.read_text(encoding='utf-8').strip()
        if k:
            return k, str(kf)
    print('ERROR: no API key. Set env OPENAI_API_KEY or create 06_CODE/.openai_key')
    sys.exit(2)


def rate(client, project_title, paper_title):
    user = f'project title: {project_title}\npaper title: {paper_title}'
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                response_format={'type': 'json_object'},
                messages=[{'role': 'system', 'content': SYSTEM_PROMPT},
                          {'role': 'user', 'content': user}],
            )
            raw = resp.choices[0].message.content.strip()
            obj = json.loads(raw)
            score = int(re.search(r'[1-4]', str(obj.get('score'))).group(0))
            rationale = str(obj.get('rationale', ''))[:300]
            return score, rationale
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError('unreachable')


def main():
    from openai import OpenAI
    key, key_src = load_key()
    client = OpenAI(api_key=key)
    print(f'[cfg] model={MODEL} temperature={TEMPERATURE} prompt={PROMPT_VERSION} key_src={key_src}')

    ann = pd.read_csv(SRC_ANN)
    done = {}
    if OUT_CSV.exists():
        prev = pd.read_csv(OUT_CSV)
        done = {int(r.pair_id): (int(r.llm_score), str(r.llm_rationale)) for r in prev.itertuples() if pd.notna(r.llm_score)}
        print(f'[resume] {len(done)}/150 already rated')

    rows = []
    for i, r in enumerate(ann.itertuples(), 1):
        pid = int(r.pair_id)
        if pid in done:
            s, why = done[pid]
        else:
            s, why = rate(client, str(r.project_title), str(r.paper_title))
            done[pid] = (s, why)
            time.sleep(0.3)
        rows.append({'pair_id': pid, 'llm_score': s, 'llm_rationale': why,
                     'model': MODEL, 'prompt_version': PROMPT_VERSION})
        if i % 25 == 0:
            pd.DataFrame(rows).sort_values('pair_id').to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
            print(f'[checkpoint] {i}/150 rated')

    res = pd.DataFrame(rows).sort_values('pair_id').reset_index(drop=True)
    res.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
    print(f'[done] wrote {OUT_CSV} ({len(res)} rows)')

    # ---- agreement stats (secondary evidence) ----
    from sklearn.metrics import cohen_kappa_score, confusion_matrix
    from scipy.stats import spearmanr
    m = ann[['pair_id', 'annotator1_score']].merge(res[['pair_id', 'llm_score']], on='pair_id')
    h = m['annotator1_score'].astype(int)
    l = m['llm_score'].astype(int)
    kappa = cohen_kappa_score(h, l, weights='quadratic')
    rho_hl, p_hl = spearmanr(h, l)
    exact = float((h == l).mean())
    cm = confusion_matrix(h, l, labels=[1, 2, 3, 4])
    cm_df = pd.DataFrame(cm, index=['human1', 'human2', 'human3', 'human4'],
                         columns=['llm1', 'llm2', 'llm3', 'llm4'])

    cos = pd.read_csv(COS_CSV)
    tri = cos.merge(m, on='pair_id')
    rho_rtas_llm, p_rtas_llm = spearmanr(tri['cos_mini'], tri['llm_score'])

    agg = pd.DataFrame([
        ('n_pairs', len(m), 'all 150 pairs'),
        ('human_llm_quadratic_weighted_kappa', kappa, 'annotator1 vs LLM (gpt-4o, temp=0, blind)'),
        ('human_llm_spearman_rho', rho_hl, 'human vs LLM rank agreement'),
        ('human_llm_spearman_p', p_hl, 'asymptotic p'),
        ('human_llm_exact_agreement', exact, 'share of identical 1-4 scores'),
        ('rtas_llm_spearman_rho', rho_rtas_llm, 'triangulation: cos vs LLM score'),
        ('rtas_llm_spearman_p', p_rtas_llm, 'asymptotic p'),
        ('rtas_human_spearman_frozen', 0.405, 'frozen C1 reference (not recomputed here)'),
    ], columns=['stat', 'value', 'note'])
    agg.to_csv(AGG_CSV, index=False, encoding='utf-8-sig')
    print()
    print(agg.to_string(index=False))
    print()
    print('[confusion matrix human x llm]')
    print(cm_df.to_string())
    print()
    print(f'[done] wrote {AGG_CSV}')


if __name__ == '__main__':
    main()
