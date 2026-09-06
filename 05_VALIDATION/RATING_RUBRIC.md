# 150 对人工验证：评分 Rubric 与严谨度加固协议（v1.0-cand.9）

**性质声明：本文件及由此产生的全部分析均为 secondary / robustness 材料，不改动冻结主链的任何统计数值（冻结点估计 ρ_s = +0.405 保持不变）。**

任务背景：150 对（项目标题，论文标题）配对用于 RTAS 的构造效度检验（C1）。配对为随机构造（非刻意挑选），人工评分分布 1 分 ×134 / 2 分 ×13 / 3 分 ×2 / 4 分 ×1。人工评分由单一评分者（作者本人）完成，英文稿口径为 **single-rater reference relevance ratings**（禁写 human validation / inter-rater reliability）。

---

## 1. 评分 Rubric（1–4 锚点定义）

任务：**仅依据两个标题的文本信息**，判断论文与项目研究主题的语义相关程度。不提供摘要、引用数、年份、学院信息；评分时**不可见** RTAS / 余弦相似度数值与首轮评分（盲评）。

| 分数 | 锚点（英文，与 LLM prompt v1 逐字一致） | 中文说明与实例（来自已标注对） |
|------|------------------------------------------|-------------------------------|
| **4** | Directly relevant: same research problem, or directly supporting method/data. | 同一研究问题，或直接支撑的方法/数据。例：新冠疫情特大城市夜间灯光分析 ↔ 语义变化检测网络 |
| **3** | Substantially relevant: same problem area or same methodology domain, clear overlap. | 同一问题域或同一方法学领域，明显重叠。例：北斗/GNSS 协同定位 ↔ 全球 XCO2 遥感制图；植物识别 APP ↔ 滑坡清单自动检测 |
| **2** | Weakly relevant: shares a broad discipline or generic methods, but different problems. | 共享大口径学科或通用方法，但研究问题不同。例：MRAM 微磁仿真 ↔ 粒子分支比测量；古壁画修复深度网络 ↔ 城市土地利用制图 |
| **1** | Not relevant: no meaningful semantic connection. | 无实质语义联系（随机配对的典型结果） |

---

## 2. 已完成的统计稳健化（R1–R6，`06_CODE/11_validation_robustness.py`，seed 42）

结果文件：`human_validation/robustness/validation_robustness_stats.csv`；每对余弦值：`robustness/150pairs_with_cos_mini.csv`（150/150 精确标题匹配，ρ 复现 +0.4055 ✓）。

| 统计量 | 值 | 说明 |
|---|---|---|
| Spearman ρ（冻结点估计） | **+0.405** | 渐近 p = 2.6×10⁻⁷ |
| R1 Bootstrap 95% CI | **[+0.281, +0.509]** | B=10,000 对重抽样，不含 0 |
| R3 置换检验 p | **< .001**（9.999×10⁻⁵） | B=10,000，符号置换 |
| R2 Kendall τ-b | **+0.327** [+0.229, +0.410] | 秩一致性的第二统计量 |
| R4 二分判别 **AUC** | **0.880** [0.793, 0.949] | 评分≥2 vs =1；直接回应"134 个 1 分"质疑：余弦对"人工判定相关/不相关"的判别力强 |
| R4 点二列相关 r_pb | +0.459 | 同上二分的连续版本 |
| R6 逐对剔除影响 | max \|Δρ\| = 0.018 | 无单点驱动 |
| R5 仅相关子集（n=16）ρ | −0.253 | **仅透明报告**：n 过小不作推断；本验证的效力主张建立在 AUC（相关 vs 不相关判别）与全样本秩相关上，不主张在"相关对内部"精细排序 |

英文稿可写（示例）：
> Because 134 of 150 pairs were rated 1 (random pairings are expected to be irrelevant), we additionally report a dichotomized analysis: the embedding-level cosine separates rater-identified relevant (≥2) from irrelevant (=1) pairs with AUC = 0.88 (95% bootstrap CI [0.79, 0.95], 10,000 resamples, seed 42), and the overall Spearman correlation is robust to leave-one-out deletion (max |Δρ| = 0.02) with a permutation p < .001.

---

## 3. LLM 第二评分协议（已实现，`06_CODE/12_llm_second_rater.py`）

- 填补标注文件中预留但从未执行的 `annotator2_score` 槽位（新文件 `150pairs_llm_second_rater.csv`，不改原文件）。
- **盲评**：模型仅见 `project_title` + `paper_title`；不可见人工分数、余弦值、引用数、学院/级别。
- **确定性**：model = gpt-4o，temperature = 0，JSON 输出，prompt **v1**（系统提示词即上表英文锚点 + 输出格式，逐字存于脚本 `SYSTEM_PROMPT`）。
- 报告口径：human–LLM **agreement**（quadratic weighted κ、Spearman、完全一致率），以及 RTAS–LLM 三角验证 Spearman（与冻结 RTAS–human +0.405 对照）。
- **禁止表述**：LLM 一致性 ≠ inter-rater reliability ≠ 重测信度；三者分别报告，英文稿标 *human–LLM agreement (secondary evidence)*。

结果文件：`human_validation/robustness/llm_agreement_stats.csv`。

## 4. 重测信度协议（intra-rater test–retest，待执行）

- 表单：`retest_40pairs_form.csv`（seed 42 从 150 对抽 40 对，呈现顺序已打乱；不含首轮分数）。
- 执行：**≥2 周洗脱期后**，同一评分者仅依据本表单标题盲评（不看首轮任何分数、不看 RTAS）。
- 统计：quadratic weighted κ（首轮 vs 重测）+ Spearman；随洗脱期长度一并报告。
- 协议冻结：本文件与表单先于重测评分提交仓库（时间戳 commit），重测为 pre-specified。

## 5. 第二人类评分者协议（可选，待招募）

- 表单：`second_rater_50pairs_form.csv`（seed 42 独立抽 50 对，不含人工首轮分数与任何提示）。
- 执行：第二名评分者仅读第 1 节 rubric 后独立评分；双方不互看分数。
- 统计：quadratic weighted κ + Spearman（第二评分者 vs 首轮评分者）。
- 意义：若完成，英文稿可将验证描述升级为 "a 50-pair subsample was independently rated by a second rater (quadratic weighted κ = ...)"；未完成不阻塞投稿（第 2–4 节证据已足）。

## 6. 冻结纪律

- ρ_s = +0.405 及全部冻结 CSV 数值不变；本目录所有输出均为新增 secondary 文件。
- 所有随机抽样 seed = 42；脚本：`06_CODE/11_validation_robustness.py`、`06_CODE/12_llm_second_rater.py`。
