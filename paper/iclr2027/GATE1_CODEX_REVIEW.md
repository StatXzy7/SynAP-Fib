# GATE1_CODEX_REVIEW — Codex Gate 1 独立审查记录

**日期**: 2026-09-05
**审查方**: Codex(MCP `mcp__codex__codex` / `mcp__codex__codex-reply`,thread `01a07112-ef0b-7363-a1e6-c6098f70a6c4`)
**被审对象**: `paper-plan/05_manuscript/synap_fib_tmi_20260904/` 主稿 + 补充材料(Phase 1 全部文稿)
**执行方**: Claude Code(ZCode 侧);按 `AGENTS.md` §5 与 `reviewer-routing.md`,审查侧为 Codex,跨模型独立性成立

## 一、输入版本

- 稿件状态:Phase 1 完成稿 —— main.tex + sections/01–05 + tables/I–IV + figures/fig1_architecture.tex(占位)+ supplementary.tex + references.bib(28 条,richter2025basel 已按 Crossref 修正补全至 17 位作者)。
- FACTS.md:含 §10.1 负责人确认事实(2026-09-04);richter2025basel 元数据于 2026-09-05 更正为 14(1):Art.83。
- 编译基线:main.pdf 9 页,0 error / 0 Overfull / 3 Underfull(main.log);supplementary.pdf 3 页无 error。
- **提交过程记录**:第 1 次提交(thread `01a0710f…`)因 Codex 沙箱文件访问被拒(`CreateProcessAsUserW failed: 5`),Codex 正确拒绝在未读文件情况下给判定,结果为 NOT ASSESSED;第 2 次提交因模板占位符未展开被 Codex 识破(FAIL:placeholders);第 3 次以**全文内联**方式提交成功并获完整审查。前两次失败均如实记录,不构成有效审查。
- 审查提示包含完整 A–G 清单、三个已知问题(DORN 归因、Positioning gap 声明、SHA-MTL regularizer 转述)及执行方自审摘录(标注"verify, do not trust")。

## 二、Codex 判定

> ## Verdict
> **FAIL** — The manuscript contains unresolved hard-rule violations and claim–evidence mismatches, including the DORN misattribution, an unapproved novelty-adjacent claim, unsupported quantitative statements, an incorrect split description, and limitations that do not follow the mandated three-paragraph tiering.

**发现统计(2026-09-05 核正)**:共 15 项 —— **1 CRITICAL、9 HIGH、2 MEDIUM、3 LOW**(Finding 1 = CRITICAL;Findings 2–10 = HIGH;11–12 = MEDIUM;13–15 = LOW。先前执行方汇总中的 "8 HIGH / 3 MEDIUM / 2 LOW" 为误计,以本条为准)。

## 三、审查发现(15 项,原文全文)

**Finding 1 — CRITICAL** · `sections/02_related_work.tex` "Ordinal and fine-grained prediction"
> "A second family discretizes a continuous quantity into ordered bins and regresses the expectation over the resulting distribution, as in ordinal depth estimation~\cite{dorn2018}."

DORN 用累积概率阈值 + 区间中点解码,非 softmax 期望(arXiv 1806.02446)。要求:改为 "…predicts a per-bin probability distribution, as in ordinal depth estimation~\cite{dorn2018}";本文自身 Eq. (1) 的期望表述不构成 DORN 误归因。

**Finding 2 — HIGH** · `sections/02_related_work.tex` "Positioning"
Gap 声明("What has not been characterized, to the extent that the literature above reflects…")保留语不足以移除文献空白断言;按 DECISIONS.md §6.2 需负责人明确批准或改写为研究问题表述。紧邻句 "Prior work generally reports a single auxiliary signal in its favourable configuration" 亦偏宽,需充分引文支持。

**Finding 3 — HIGH** · `sections/02_related_work.tex` 多任务段
"the segmentation branch acts as a representational regularizer~\cite{zhou2020mtlabus,shamtl2021}" 在当前强度下为 overstatement;两篇摘要支持联合学习改善双任务,不建立该机制。建议改写为经验性描述,保留 "regularizer" 仅当原文直接支持并明示为解释。

**Finding 4 — HIGH** · `sections/03_methods.tex` 数据集节
六切面详细描述与 "One to three images are acquired per plane" 未记录于 FACTS.md,违反 DECISIONS.md §5 单一事实源;需经 Phase 0 fact-maintenance 补录或删除。

**Finding 5 — HIGH** · Methods / Table I / Results
"the same centers are represented across all splits" 与 FACTS.md 不符(train 35 centers、val 33、test 4;仅证实四个 test centers 均在 train)。要求改为:"All four centers represented in the test set also appear in the training split; the split is patient-disjoint but center-shared."(Methods 原文已正确;Results §A 与 Table I 标题需改。)

**Finding 6 — HIGH** · `sections/04_results.tex` 队列节
首句事实性错误(同 Finding 5);后半 "rather than on unseen institutions" 被指为禁用表述框架,建议仅以结构事实表述 scope 限制。(注:该句为否定式披露,DECISIONS.md §3.4 允许并要求在 Methods/Limitations 披露;Codex 建议更保守措辞 —— 列入负责人裁量项。)

**Finding 7 — HIGH** · `sections/03_methods.tex` 训练环境
RTX 5090 D / CUDA 12.8 / PyTorch 2.11.0 / torchvision 0.26.0 / Python 3.10 未记录于 FACTS.md;需补录或删除(含 GPU 型号中的数字)。

**Finding 8 — HIGH** · `figures/fig1_architecture.tex` Figure 1 标题
"36-bin ordinal posterior via 35 binary logistic units" 的 "35 binary logistic units" 未记录于 FACTS.md 且未对实现核验;图仍为占位、未按 DECISIONS.md §4.2 以 draw.io 绘制。要求:补录并核验后才可写;替换占位图;不得暗示未做的组件消融。

**Finding 9 — HIGH** · `sections/05_discussion.tex` Limitations
DECISIONS.md §5.1 要求三段式主题结构,现稿为四段(参考标准/弱框 caveat 独立成段)。要求合并进三段结构,或获负责人对结构性偏差的批准。

**Finding 10 — HIGH** · Limitations 第 1 段
"does not establish generalization to unseen institutions or acquisition environments, which would require dedicated external validation" 建议改为以结构事实表述("test centers are also represented in training, so the study does not establish performance at centers absent from training"),避免把 "external validation" 作为当前实验属性呈现。

**Finding 11 — MEDIUM** · `tables/table4_auxiliary.tex` 标题
标题称 "unrounded values are given in the Supplementary Material",但补充材料仅提供参数/GFLOPs/延迟的未取整值;position acc/CE、Dice/IoU 未取整值(F-POS/F-LES 有:0.662250/0.944391/0.353920/0.226066/0.360312/0.235487 等)未列入。要求补入补充材料或修改标题措辞。

**Finding 12 — MEDIUM** · `sections/05_discussion.tex` Interpretation
"a position estimate permits automatic checking that the standardized six-position protocol was followed, and a localization map gives the reader something to inspect" 建议降为潜在用途("could support" / "may provide"),不暗示已验证的筛查效用(position accuracy 66.81%,弱框 agreement only)。

**Finding 13 — LOW** · `sections/04_results.tex` checkpoint 诊断节
该节为 test-informed 诊断对比,非预登记主结果;需确保不被读作事后 checkpoint 分析或暗示 epoch 120 为竞争性选择。

**Finding 14 — LOW** · `SELF_AUDIT.md` 条目 1
自审将 0.944391 标注为 AUROC,实为 arm C 的 position-branch cross-entropy。非稿件错误,但表明执行方数字审计不完全可靠。(已在本文档记录更正,不改历史自审文件。)

**Finding 15 — LOW** · `references.bib`
28 条 vs 45–60 指导区间(非硬性);Gate 2 须对全部引文执行四轴审计(存在性/元数据/位置支持/结论强度)。不为凑数加引文。

## 四、三问答复

1. **DORN 修法足够吗?** 足够(该句);本文 Eq. (1) 合法,非 DORN 误归因;但修前状态下仍是 Gate 1 阻塞项。
2. **Positioning gap 声明保留语足够吗?** 不足;需有可追溯记录的负责人批准,或改写/删除。
3. **SHA-MTL "representational regularizer"?** 当前强度下 overstatement;按证据改写为联合学习行为描述,除非原文直接支持且明示为解释。

## 五、Codex 指出的自审遗漏

1. 未发现 "the same centers are represented across all splits" 事实错误(35/33/4)。
2. 未发现 Methods 无 FACTS 依据的定量内容("one to three images per plane"、软硬件版本、Figure 1 的 "35 binary logistic units")。
3. 未发现 Limitations 四段式违反 §5.1 三段结构要求。
4. 未发现 Table IV 标题关于补充材料含未取整 branch 指标的失实声明。
5. 未发现筛查效用措辞越界(自动协议核查/读者可视化)。
6. 自审将 0.944391 误标为 AUROC(实为 CE)。
7. DORN 误归因确认但"延后修"不被 Gate 1 接受;novelty 声明未按当前审批阻塞项上报;"regularizer" 未升级为引文强度错配。
8. 未区分补充材料的预登记 bootstrap Δ 对照(允许)与主表禁止的 Δ 呈现(禁令不适用于补充材料的预登记对照)。
9. 未全面核验 center/split/limitations 措辞符合 Data V4 范围要求。

## 六、审查后处置(2026-09-05,执行方)

### 已执行的事实性修正(DECISIONS.md §6.1 授权范畴 + Codex 已认可措辞)

| 项 | 修改 | 依据 |
|---|---|---|
| Finding 1 | `sections/02_related_work.tex`:删去 "regresses the expectation over the resulting distribution",改为 "predicts a per-bin probability distribution" | Codex Finding 1 Required action + Q1 答复原文措辞 |
| Finding 5(部分) | `sections/04_results.tex`:"the same centers are represented across all splits" → "all four centers represented in the test set also appear in the training split"(保留后半否定式披露句) | Codex Finding 5 Required action 原文措辞;Methods 原本正确 |
| Finding 5(部分) | `tables/table1_cohort.tex` 标题:同步改为 "all four centers represented in the test set also appear in the training split" | 同上 |

修正后重编译:main.pdf 9 页,0 error,0 Overfull(3 Underfull 同前)。

### 未执行、待负责人决定(按 DECISIONS.md §6.1"改变声明强度/范围/创新性/因果含义须负责人批准")

| Finding | 建议处置 | 性质 |
|---|---|---|
| 2 | Positioning gap 声明:**批准保留** / 改写为研究问题表述 / 删除;连同 "Prior work generally reports a single auxiliary signal…" 一句的支撑核查 | 创新性声明 — 负责人批准 |
| 3 | SHA-MTL 段改写方案(两选):(a) "Joint segmentation and classification has been studied in breast ultrasound, where joint learning improves outcomes of both tasks~\cite{zhou2020mtlabus,shamtl2021}";(b) 保留 "acts as a representational regularizer" 但明示为解释性转述 | **UNRESOLVED** — 引文强度;负责人决定前不得视为通过;执行方建议 (a) |
| 6(后半)/10 | Limitations 及 Results 否定式披露句是否按 Codex 建议进一步改为纯结构事实表述 | 披露措辞 — 负责人裁量;现行措辞依 DECISIONS.md §3.4 属要求的否定式披露 |
| 9 | Limitations 三段式重构(参考标准/弱框 caveat 并入)或批准四段结构偏差 | 结构 — 负责人批准 |
| 12 | 筛查效用句降格("could support"/"may provide") | 声明强度 — 负责人批准 |

### 待 Phase 0 fact-maintenance 补录(补录后无需改稿或仅需微调)

| Finding | 需补录事实 | 来源 |
|---|---|---|
| 4 | 六切面逐条定义 + "One to three images are acquired per plane" | P1 审计第四部分 A2(数据清洗要点规则 1 + 旧稿,负责人已签核 P1 关闭);需正式录入 FACTS.md |
| 7 | RTX 5090 D / CUDA 12.8 / PyTorch 2.11.0 / torchvision 0.26.0 / Python 3.10 / AMP | FORMAL_PROTOCOL/运行环境工件;P1 审计 D7/D8 |
| 8 | "35 binary logistic units"(须先对实现核验再补录) | 冻结实验代码(只读核验) |
| 11 | Table IV 各 branch 指标未取整值列入补充材料(值已在 FACTS.md F-POS/F-LES) | FACTS.md §5 |

## 七、Gate 1 状态

**FAIL(2026-09-05,thread 01a07112)**。三项已修(Finding 1、5 全部、部分 6 的首句事实错误);其余 11 项待负责人决定或 fact-maintenance 补录。**修复全部发现后需重新提交 Gate 1 复审(round 2)方可 PASS。**

## 八、未关闭问题清单(移交下一轮)

1. Finding 2 — Positioning gap 声明负责人批准(或改写方案选择)。
2. Finding 3 — SHA-MTL regularizer 措辞方案选择((a) 经验性描述 / (b) 明示解释)。**UNRESOLVED。**
3. Finding 4/7/8 — FACTS.md 补录三项(六切面、软硬件、35 binary logistic units),其中 35 units 须先对冻结实现核验。
4. Finding 9 — Limitations 三段式重构方案或结构偏差批准。
5. Finding 11 — 补充材料补未取整 branch 指标或改 Table IV 标题。
6. Finding 12 — 筛查效用措辞降格批准。
7. Finding 13 — checkpoint 诊断节的呈现分隔(可与其他项一并处理)。
8. Finding 15 — Gate 2 全引文四轴审计(45–60 目标区间,不为凑数加引文)。
9. 上述修复完成后重新编译 + 重新提交 Codex Gate 1 round 2。

## 九、负责人决定记录(2026-09-05 已全部决定)

以下五项为 Gate 1 处置所需的负责人明确决定。**全部五项已于 2026-09-05 决定**;执行状态见表。

| # | 决定项 | 选项 | 执行方建议 | 决定 | 日期 | 执行状态 |
|---|---|---|---|---|---|---|
| D1 | **Positioning gap 声明**(Finding 2) | (i) 批准保留现句;(ii) 改写为研究问题表述;(iii) 删除 | — | **(iii) 删除** | 2026-09-05 | ✅ 已执行(整句删除,段落其余部分保留) |
| D2 | **SHA-MTL regularizer 措辞**(Finding 3) | (a) 改写为 "joint learning improves outcomes of both tasks"(经验性描述);(b) 保留并明示为解释性转述 | (a) | **(a)** | 2026-09-05 | ✅ 已执行 |
| D3 | **Limitations 结构**(Finding 9) | (i) 按 DECISIONS.md §5.1 重构为三段;(ii) 批准四段结构偏差 | (i) | **(ii) 批准四段偏差** | 2026-09-05 | ✅ 记录批准,无文本改动 |
| D4 | **筛查效用措辞**(Finding 12) | (i) 降格为 "could support / may provide";(ii) 保留现句 | (i) | **(ii) 维持现行** | 2026-09-05 | ✅ 记录决定,无文本改动 |
| D5 | **Results/Limitations scope 披露措辞**(Findings 6 后半 / 10) | (i) 维持现行否定式披露;(ii) 按 Codex 建议改为纯结构事实表述 | (i) | **(i) 两项均维持现行** | 2026-09-05 | ✅ 记录决定,无文本改动 |

**决定后执行序列(2026-09-05,全部执行完毕)**:

1. ✅ 按 D1/D2 更新 `sections/02_related_work.tex`(gap 句删除、SHA-MTL 句改写);
2. ✅ FACTS.md 补录(Finding 4/7/8):§2.3 采集协议(F-ACQ-PROTOCOL 六切面、F-ACQ-PER-PLANE 每切面 1–3 图;provenance = P1 签核 + 数据清洗要点规则 1 + 旧稿 Data Collection)、F-DESIGN-ENV(训练环境,provenance = 冻结 `runtime_benchmark_results.json` + `environment.yml`,已对冻结树只读核验)、F-DESIGN-HEAD(grading head = 单个 36-unit 线性层 + softmax,provenance = 冻结 `model.py:60-69` + `prediction.py:38-41`;**核验发现 "35 binary logistic units" 为错误描述**,Figure 1 标题已同步修正为 "via a linear output layer");
3. ✅ Table IV 未取整 branch 指标已补入补充材料(新表 `tab:unroundaux`,值为 FACTS.md §5 记录精度:0.662250 / 0.665861 / 0.944391 / 0.916542 / 0.353920 / 0.360312 / 0.226066 / 0.235487);
4. ✅ Results 的 stage-balanced 已改为纯观察性表述("Because each of the four stages contributes 60 of the 240 test patients, …";60 与 240 均为 FACTS.md 值;Methods 中平行句保留 FACTS.md 许可框架,已提请 round 2 reviewer 判断是否一致);
5. ✅ 重新编译:main.pdf 9 页 / 0 error / 0 Overfull(3 Underfull 同前);supplementary.pdf 3 页 / 0 error / 0 Overfull;
6. ⏳ 已提交 Codex Gate 1 round 2(同线程,变更集 15 项逐条列明),结果待返回后将追加 round 2 章节。

## 十、Gate 1 Round 2(2026-09-05,同线程)

**输入**:Round 1 后的全部处置变更集(§九 D1–D5 决定执行 + fact-maintenance 补录 + 补充材料未取整指标 + 重编译);逐项列明 15 项变更,要求 reviewer 对 Finding 1–15 逐项判定 RESOLVED / RESOLVED-BY-SUPERVISOR-DECISION / OPEN,并检查修改是否引入新问题。

### 判定

> **PASS-WITH-CONDITIONS** — Findings 1–14 are resolved or explicitly accepted by supervisor decision; Finding 15 remains deferred to Gate 2, and the shortened Positioning paragraph still contains one broad, insufficiently supported literature generalization.

### 逐项判定摘要

| Finding | 判定 |
|---|---|
| 1 DORN | RESOLVED |
| 2 Positioning gap 句 | RESOLVED-BY-SUPERVISOR-DECISION(D1 删除);**遗留一项 MEDIUM 见下** |
| 3 SHA-MTL | RESOLVED-BY-SUPERVISOR-DECISION(D2 (a)) |
| 4 六切面/每切面图像数 | RESOLVED(FACTS §2.3) |
| 5 center-sharing | RESOLVED |
| 6 scope 披露 | RESOLVED-BY-SUPERVISOR-DECISION(D5;须保持限定于 scope 披露,不得扩散或转写为外部中心稳健性证据) |
| 7 训练环境 | RESOLVED(F-DESIGN-ENV) |
| 8 Figure 1 标题 | RESOLVED(F-DESIGN-HEAD;**图本身仍为占位** —— P3 制作项,非措辞缺陷) |
| 9 Limitations 四段 | RESOLVED-BY-SUPERVISOR-DECISION(D3 批准偏差) |
| 10 披露句 | RESOLVED-BY-SUPERVISOR-DECISION(D5) |
| 11 Table IV 未取整 | RESOLVED(补充材料新表) |
| 12 筛查效用 | RESOLVED-BY-SUPERVISOR-DECISION(D4;**不得再增强**,摘要/结论/图题不得追加效用声明) |
| 13 checkpoint 诊断 | RESOLVED(独立小节 + 明示规则未事后替换) |
| 14 自审 AUROC 误标 | RESOLVED-BY-SUPERVISOR-DECISION(更正记录可检索;"AUROC" 误标不得复用) |
| 15 全引文审计 | **OPEN — 按计划移交 Gate 2** |

### 修改后新问题

1. **MEDIUM — Positioning 段遗留的宽泛概括**:删除 gap 句后,"Prior work generally reports a single auxiliary signal in its favourable configuration" 承担了更多定位负担,仍是文献级概括。**条件(Gate 2 处理)**:或添加直接支持的引文,或软化为有界观察("Several of the closely related studies considered here use a single auxiliary signal…")。**属声明强度类,须负责人在 Gate 2 决定。**
2. LOW — 段落连贯性:缩短后仍连贯;"yields an answer that a single-prior study could not have surfaced" 是关于比较所提供信息的逻辑表述,非 novelty 声明。无需改动。
3. LOW — stage-balanced 措辞一致性:Methods(FACTS 许可框架)与 Results(纯观察性)两处"无实质不一致";条件:两处均保持观察性,不得改为 "intentionally balanced / designed to balance / stratified by construction"。
4. LOW — D4 保留的效用措辞为已接受的残留风险;不得在摘要/结论/图题增强。
5. LOW — Figure 1 仍为占位;**P3 集成前必须完成 draw.io 图**(.drawio + .pdf 双工件)。

### Gate 1 通过条件(全部登记)

1. Gate 2 完成全引文四轴审计(存在性/元数据/句级支持/转述强度)。
2. "Prior work generally reports a single auxiliary signal…" 加引文支持或软化(负责人决定)。
3. 最终制作集成前替换 Figure 1 占位图。
4. 保持负责人批准的 Limitations/效用措辞,不得扩大范围。

### 结论

**Gate 1 = PASS-WITH-CONDITIONS(2026-09-05)**。条件 1、2 归 Gate 2;条件 3 归 P3;条件 4 为持续约束。Phase 1 的 Discussion+Limitations+Conclusion 审查通过,工作流可进入 Phase 2(集成、参考文献、构建 → Gate 2)。

*Round 2 审查原文已完整保存于本节;输入变更集见 §九执行记录。未修改冻结实验产物;未运行 git;未访问 test。*
