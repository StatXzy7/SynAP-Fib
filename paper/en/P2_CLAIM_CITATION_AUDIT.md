# P2_CLAIM_CITATION_AUDIT — 声明与引文审计

**审计日期**: 2026-09-04
**审计对象**: 主稿(sections/ + main.tex)28 条引文、全部正文声明
**方法**: (1) cite-key ↔ bib 交叉核对(脚本化);(2) 每条 DOI 经 Crossref/OpenAlex 核验题名/年份/卷期;(3) 逐条抓取被引论文摘要,对照稿件句子做 attribution-support 判断;(4) 全稿禁用声明扫描。

---

## 一、引文完整性(机器验证)

| 检查 | 结果 |
|---|---|
| cite-key ↔ bib 条目 | ✅ 28/28 完全一致,零缺失、零未引用 |
| DOI 解析 → 题名一致 | ✅ 全部(26 条有 DOI + 2 条图书/标准无 DOI 属预期) |
| LaTeX 编译 | ✅ 0 error / 0 overfull / 0 undefined,9 页 |
| 年份一致性 | ✅ 修正后 26/26 OK(见下) |

## 二、发现并已修正的错误(4 处年份 + 1 处 DOI 元数据 + 1 处严重 attribution 错误)

| # | 条目 | 问题 | 修正 |
|---|---|---|---|
| 1 | `agmbtransformer2021` 年份 | bib 写 2021(online-first),正式卷期 JBHI 26(4) = **2022** | 已改 2022 |
| 2 | `petsnet2023` 年份 | bib 写 2023(online),TMI 43(3) = **2024** | 已改 2024 |
| 3 | `zhou2020mtlabus` 年份 | bib 写 2020(online 2020-11-28),MIA vol 70 = **2021** | 已改 2021;页码 `101918--101918` → `101918` |
| 4 | `unimodalbeta2021` 年份 | bib 写 2021(online),PatCog 122 = **2022** | 已改 2022;页码同理 |
| 5 | `richter2025basel` 元数据 | 卷期页码错误(14(4):67–76)、无 DOI、作者截断为 "and others" | 改为 **14(1):83, DOI 10.1186/s40249-025-01349-x**,补全作者(Richter…Tamarozzi, Wu) |
| 6 | **`agmbtransformer2021` attribution** | 稿件称 "bone-age assessment";**该论文实际是 root canal therapy 评估** | 已改为 "automated evaluation of root canal therapy" |

错误 #6 是本次审计最重要的发现——典型 "真论文 + 错 attribution",若进入投稿将直接损害可信度。来源:稿件撰写阶段从记忆归类时混淆(AGMB 的解剖引导多分支结构与骨龄评估网络确有相似性,但该特定论文是牙科 X 线根管治疗)。

## 三、Attribution-support 审计(逐条)

### 临床组

| 引文 | 稿件声明 | 摘要证据 | 判定 |
|---|---|---|---|
| schistoelasto2018 | TE/MRI 在流行区少有;PPF 表型 | pSWE for PPF in schistosomiasis mansoni | ✅ |
| schistopocus2024 | 超声分期系统综述 | systematic review of US staging systems | ✅ |
| swe2018staging | 准确性随设备/设置变化 | meta-analysis, pooled sensitivity/specificity | ✅ |
| interobserver2019 | 观察者间一致性是公认问题 | interobserver reproducibility of SWE staging | ✅ |
| usfibrosisgan2022 | 生成式增强补偿有限数据 | "A data augmentation method based on a GAN model was used" | ✅ |
| microflow2023 | 造影微流输入 | title: contrast-enhanced micro-flow cines | ✅ |
| hfus2025 | 高频采集暴露细微纹理 | high- vs low-frequency paired comparison | ✅ |
| liverspleen2025 | 配对器官视角 | title: Paired liver–spleen … network | ✅ |
| richter2025basel | 国际指南对应关系在 Basel 协议中描述 | WHO expert meeting protocol | ✅ |
| xu2026sfibai | 36 级 posterior 期望;江苏入组;入组标准 | 摘要含 multicentre/36-level;期望表述在正文 §Methods(line 91 of final tex);江苏在 line 301 | ✅ |

### 序数方法组

| 引文 | 稿件声明 | 摘要证据 | 判定 |
|---|---|---|---|
| coral2020 | 架构式 rank consistency | weight-sharing constraint(架构约束)→ rank-monotonicity | ✅ "architecturally" 成立 |
| corn2023 | 条件概率分解 | conditional training sets → unconditional rank probabilities | ✅ |
| dorn2018 | 离散化+期望回归 | SID 离散化 + softmax 期望 | ✅ |
| unimodalbeta2021 | unimodal 正则 | beta-distribution unimodal regularisation | ✅ |
| sonnet2022 | 分级+分割联合 | nuclei segmentation+classification, ordinal | ✅ |
| drgraduate2020 | 不确定性感知视网膜分级 | uncertainty + DR grading | ✅ |

### 解剖先验/多任务组

| 引文 | 稿件声明 | 摘要证据 | 判定 |
|---|---|---|---|
| attentiongated2019 | 无显式定位监督的注意力 | "eliminate the necessity of explicit external localisation modules" | ✅ |
| anatomyxnet2022 | 解剖分割掩码监督注意力 | organ-level annotations → anatomy-aware attention | ✅ |
| agmbtransformer2021 | ~~骨龄~~ → **根管治疗**(已修正) | root canal therapy, anatomy-guided multi-branch | ✅(修正后) |
| opticdisc2020 | 杯盘包含关系引导 | anatomical knowledge to guide segmentation | ✅ |
| hovertrans2023 | 水平/垂直组织分层入注意力 | inter-/intra-layer horizontal+vertical | ✅ |
| zhou2020mtlabus | 乳腺超声分割+分类联合 | title: MTL segmentation+classification ABUS | ✅(title 级) |
| shamtl2021 | 分割分支作为表征正则 | soft/hard attention MTL;"regularizer" 为合理转述 | ✅(转述可接受) |
| petsnet2023 | 胎脑 pose+分割联合 | joint pose estimation + tissue segmentation | ✅ |
| covidweak2020 | 图像级监督的弱定位 | weakly-supervised, lesion localization | ✅ |
| weakbreast3d2019 | 同上 | weakly supervised, localizing lesions | ✅ |

### 需说明的判定边界

- **zhou2020mtlabus / shamtl2021 / microflow2023 / liverspleen2025** 无公开摘要(OpenAlex/S2 均缺),支持证据为**题名级**。四条声明均为描述性("做 X")而非结论性("X 提升 Y"),题名足以支撑。风险低。
- **shamtl2021 的 "representational regularizer"**:这是对多任务分割分支作用的**解释性转述**,非原文原话。属于学界通行表述,不构成 overclaim。
- **xu2026sfibai 的 "expectation"**:摘要未用该词,但**正式发表正文**明确写 "the final fibrosis score is obtained by computing the weighted expectation of this distribution"。该引用为项目负责人自己的论文,查证了投稿版全文。

## 四、声明强度扫描(修正后全文)

| 扫描词 | 命中 | 判定 |
|---|---|---|
| significantly better / significant improvement | 0 | ✅ |
| interaction effect / factorial | 0 | ✅ |
| state-of-the-art / novel / first to | 0 | ✅ |
| proven / 因果措辞 | 0 | ✅ |
| outperform | 1 | 同 arm 内 best vs last(合法) |
| unseen center(否定式) | 2 | "rather than to estimate performance on unseen centers" / "not to estimate" |
| external validation(否定式) | 1 | Limitations:"would require dedicated external validation" |
| 标注者姓名/人数 | 0 | ✅(P1 匿名约束维持) |
| 旧 SFibAI 性能数字(0.116/93.9%/167,702 等) | 0(正文) | ✅;注意 xu2026sfibai 的**摘要本身**含这些数字——我们引用它属方法归属,不在正文复述其数值 |

## 五、遗留事项(移交 P3)

1. Fig 1(架构图 draw.io)、Fig 2(队列图)、Fig 4(混淆+校准)、Fig 5(定性)与 Supp Fig S1–S3 待制作;
2. Abstract 待 Results 冻结后撰写(当前占位);
3. 补充材料 "Figure 3" 编号错位 → P3 插图后统一;
4. supplementary S10–S12 版面优化。

## 六、P2 关闭条件判定

**✅ P2 达到关闭条件。**

- 28 条引文:存在性 ✅、元数据 ✅(修正 5 处)、支持关系 ✅(修正 1 处严重 attribution 错误);
- 声明强度:禁用声明零出现;所有否定式披露措辞符合 DECISIONS.md;
- 编译干净(9 页,0/0/0)。

审计工件:`scripts/citecheck.py`、`scripts/citecontext.py`、`scripts/verify_dois.py`、`scripts/fetch_abstracts.py`、`scripts/fetch_abstracts_s2.py`、`tables/cited_abstracts.json`(26 条被引论文摘要快照)。

---

## 七、2026-09-05 定点补核(P2 收口 + Gate 1 提交前)

按负责人指令执行的五项补核。方法:重新运行 DOI 验证(`scripts/verify_dois.py`,Crossref 在线核对),对争议条目直接抓取原始来源(Crossref API、arXiv 全文 PDF、Semantic Scholar、Springer 页面经 Jina reader)。

### 7.1 Gate 1 既有结论核查

- **查找结果(2026-09-05 上午):Gate 1 此前无任何有效记录。** `FACTS.md` §11 记录 Gate 0 = PASS;`SELF_AUDIT.md` 标注 "AWAITING CODEX GATE 1";本审计(§六)为执行侧自审,不构成 Gate 1 通过。
- **处理:已提交。** 2026-09-05 经 Codex MCP 提交(three 次尝试:两次失败——文件访问被拒、模板占位符未展开;第三次全文内联成功)。**Round 1 结果:FAIL,15 项发现**(1 CRITICAL / 9 HIGH / 2 MEDIUM / 3 LOW;先前本节所写 "8 HIGH / 3 MEDIUM / 2 LOW" 为误计,已核正),详见 `GATE1_CODEX_REVIEW.md`。
- **Round 2(2026-09-05,负责人 D1–D5 决定执行后):PASS-WITH-CONDITIONS** —— Findings 1–14 全部 RESOLVED 或 RESOLVED-BY-SUPERVISOR-DECISION;Finding 15(全引文审计)按计划移交 Gate 2;新识别 1 项 MEDIUM 遗留条件("Prior work generally reports a single auxiliary signal…" 须在 Gate 2 加引文支持或软化,属负责人决定项)。通过条件四项见 `GATE1_CODEX_REVIEW.md` §十。
- 审查后已执行三项事实性修正(DORN 归因句、Results §A 与 Table I 标题的 center-sharing 表述),其余发现待负责人决定或 fact-maintenance 补录;**修复完成后须重新提交 Gate 1 round 2。**

### 7.2 Basel 文献(`richter2025basel`)元数据矛盾消除

- **矛盾**:本审计 §二第 5 项已将 references.bib 修正为 14(1):83 + DOI,但 `FACTS.md` §10.1 "Reference entries confirmed for reuse" 仍保留旧稿遗留的 "14(4):67–76"(该错误条目亦存在于旧稿 `SFibAI-Final2/References.bib` 第 670–679 行,作者截断为 "and others" 且无 DOI)。
- **原始来源核验(2026-09-05,Crossref API `api.crossref.org/works/10.1186/s40249-025-01349-x`)**:
  - Journal: Infectious Diseases of Poverty;**volume 14, issue 1, article number 83, year 2025**(无页码,article-number 型期刊);
  - **完整作者 17 位**(2026-09-05 复核程序化计数更正,先前误写 16):Richter, Neumayr, Garba-Djirmay, Ohmae, Aniceto, Zhou, Xu, Guo, Ning, Kamau, Tamarozzi, **Wu, King, Vennervald, Chami, Utzinger, Hatz**。
- **修正执行**:
  1. `FACTS.md` §10.1 该条目改为 14(1): Article 83, 2025, DOI 10.1186/s40249-025-01349-x,附更正说明与 Crossref 权威声明;
  2. `references.bib` `richter2025basel` 作者列表从 12 位(Wu 截止)**补全为 Crossref 的完整 17 位**(新增 King、Vennervald、Chami、Utzinger、Hatz;卷期页与 DOI 原本已正确;bib 列表本身自始正确,先前叙述中的"16 位"为计数笔误)。
- **状态**:✅ 已消除。注意:旧稿(Nature Communications 已发表版)自身引用的即是错误元数据,新稿不沿用。

### 7.3 三项归因定点核验(稿件原句 → 原文证据 → 判定)

#### (a) DORN 预测解码方式 — ❌ 稿件归因错误,需改写

- **稿件原句**(`sections/02_related_work.tex` 第 33–36 行):
  > "A second family discretizes a continuous quantity into ordered bins and regresses the expectation over the resulting distribution, as in ordinal depth estimation~\cite{dorn2018}."
- **原文位置与证据**(arXiv 1806.02446v1 全文 PDF,§3.3 "Learning and Inference",式 (5)):
  > "In the inference phase, after obtaining ordinal labels for each position of image I, the predicted depth value d̂(w,h) is decoded as: d̂(w,h) = (t_l̂ + t_{l̂+1})/2 − ξ, l̂(w,h) = Σ_{k=0}^{K−1} η(P_k(w,h) ≥ 0.5)."
- **判定**:DORN 在推理时对每个 bin 的 softmax 概率 P_k 做 **≥0.5 累加阈值**得到序数标签 l̂,再取该子区间**两端点的中点**作为深度输出;**不是** softmax 分布的期望(加权求和/soft-argmax)。稿件句中 "regresses the expectation over the resulting distribution" 对 DORN 的解码描述**不准确**。本审计 §三序数组表中 "dorn2018 | SID 离散化 + softmax 期望 | ✅" 的判定**撤销**,改为 ✗(摘要快照未含解码细节,此前误判)。
- **处理**:属措辞级归因修正,不改声明强度——建议改为 "discretizes a continuous quantity into ordered bins and predicts a per-bin probability distribution, as in ordinal depth estimation~\cite{dorn2018}"(删去 expectation 归因,保留离散化归因,后者由摘要直接支持)。该句同时是 SFibAI/本文方法与 DORN 家族对比的铺垫——本文自身用期望(式 (1)),若保留 DORN 作期望式解码的代表将构成错误归因,修正是必要的。已列入 Gate 1 提交材料请 reviewer 复核修后措辞。

#### (b) SHA-MTL / ABUS 的 representational regularizer 归因 — ❌ UNRESOLVED(负责人决定前不得视为通过;本节早先"维持可接受"的判定已被 Gate 1 推翻)

- **稿件原句**(`sections/02_related_work.tex` 第 80–83 行):
  > "Joint segmentation and classification is well established in breast ultrasound, where the segmentation branch acts as a representational regularizer~\cite{zhou2020mtlabus,shamtl2021}."
- **zhou2020mtlabus 原文证据**(Semantic Scholar 摘要,2026-09-05 获取;先前快照为空):
  > "Considering the correlation between tumor classification and segmentation, we argue that learning these two tasks jointly is able to improve the outcomes of both tasks. … the proposed multi-task framework improves tumor segmentation and classification over the single-task learning counterparts."
- **shamtl2021 原文证据**(Springer 页面摘要,经 Jina reader 获取):
  > "For the segmentation task, the sensitivity and DICE of the SHA-MTL model to the lesion regions increased by 2.27% and 1.19% compared with the single task model… The classification accuracy and F1 score increased by 2.45% and 3.82%."
- **判定(2026-09-05 统一)**:两篇原文摘要均**未使用 "regularizer" 一词**;证据支持的是"联合学习改善两个任务的表现"。本节初判("维持可接受,属转述")**与 Codex Gate 1 Finding 3(当前强度下 overstatement)冲突,以 Codex 判定为准**。**状态:UNRESOLVED——待负责人在两个方案间明确决定**:(a) 改写为经验性描述 "Joint segmentation and classification has been studied in breast ultrasound, where joint learning improves outcomes of both tasks~\cite{zhou2020mtlabus,shamtl2021}"(执行方建议);(b) 保留 "acts as a representational regularizer" 但明示为解释性转述。决定前稿件不改、不进入任何"通过"统计。
- §三序数/先验组表中 shamtl2021 "✅(转述可接受)" 的历史判定同样由本条取代。

#### (c) Positioning 研究空白声明 — ⚠️ 有保留的 gap claim,维持 SELF_AUDIT 判定:需负责人批准

- **稿件原句**(`sections/02_related_work.tex` 第 94–104 行):
  > "Individually, none of these ingredients is new: … What has not been characterized, to the extent that the literature above reflects, is how two \emph{different} anatomical priors behave when introduced into the same fine-grained grading backbone -- separately and together -- under gradient isolation. Prior work generally reports a single auxiliary signal in its favourable configuration."
- **证据情况**:"What has not been characterized" 为**文献空白断言**,无法从单篇原文核验;支持材料为 §三已审计的 26 条引文谱系(每条均为单一辅助信号配置)。保留语 "to the extent that the literature above reflects" 将断言限定于已审文献范围。
- **判定**:与 SELF_AUDIT §6 判定一致——该句是**带保留的 gap claim,功能上构成创新性主张**,按 `DECISIONS.md` §6.2 需负责人批准后方可投稿保留。不是本轮可自行关闭项;已作为未关闭问题列入 Gate 1 记录与 P3 前置事项。

### 7.4 移交记录修正(main.log vs main_final.log;补充材料 Figure~3)

- **编译日志区分**(此前审计未区分):
  - `main.log`(当前有效构建,main.pdf 9 页,295,420 字节):**0 error、0 Overfull**,3 处 Underfull hbox(badness 1708/1735/1838,段落排版);
  - `main_final.log`(旧构建,main_final.pdf 9 页,263,831 字节):**2 处 Overfull hbox**(54.3pt 表格类,line 143 附近;45.0pt 段落,lines 13–25 附近)——P1 复核记录的"当前构建 2 处 overfull"实际指向该**旧**构建;当前 main.log 无 overfull。
  - 处理:以 main.log 为准移交 P3(3 处 Underfull 为可选优化项);main_final.* 为历史构建产物。P1 审计复核章节中"2 处 overfull 为当前构建问题"的表述由本条修正——过时文件所含,不构成当前稿件缺陷。
- **补充材料 Figure~3 实际错位(保留,移交最终图序统一解决)**:`supplementary.tex` 第 253 行硬编码 "Figure~3 of the main text plots configurations A and E"。当前主稿实际仅含 2 个 figure 环境(fig1_architecture 与 fig3_stage_wise),fig3_stage_wise 现渲染为 **Figure 2**;DECISIONS.md §4.2 计划的 Figure 2(队列图)插入后其编号才会成为 3。即:该硬编码交叉引用**当前编号错位**,且未来插图增删时仍会漂移。处理:P3 插图后统一改为 \ref 或在最终编号冻结时核对;本轮不改。

### 7.5 定点补核结论

| 项 | 结果 |
|---|---|
| Gate 1 既有记录 | 无 → 本轮提交;**结果 FAIL(15 项发现)**,详见 `GATE1_CODEX_REVIEW.md` |
| Basel 元数据矛盾 | ✅ 已消除(FACTS + bib 双修,Crossref 为权威,17 位作者补全) |
| DORN 解码归因 | ❌ 稿件措辞不准确 → **Codex 认可修法,已改写**("predicts a per-bin probability distribution") |
| SHA-MTL/ABUS regularizer 归因 | ❌ **UNRESOLVED**(Codex Finding 3:当前强度下 overstatement;方案 (a)/(b) 待负责人决定,见 §7.3(b)) |
| Positioning gap 声明 | ❌ Codex 判定保留语不足;**须负责人批准或改写** |
| 编译日志区分 | ✅ 已修正移交记录(main.log 0 overfull;main_final.log 为旧构建) |
| 补充材料 Figure~3 | 保留为 P3 最终图序统一项(main.aux 证实 fig:stagewise 现渲染为 Figure 2) |

### 7.6 Gate 1 审查中超出本审计范围的发现(摘要)

Codex 另发现本审计未覆盖的问题(全文见 `GATE1_CODEX_REVIEW.md`):Methods 六切面与 "one to three images per plane" 未录入 FACTS.md(F-4);训练软硬件版本未录入 FACTS.md(F-7);Figure 1 "35 binary logistic units" 无事实依据(F-8);Limitations 四段式违反 §5.1 三段结构(F-9);Table IV 标题声称补充材料含未取整 branch 指标但实际缺失(F-11);筛查效用措辞越界(F-12);自审 0.944391 误标 AUROC(F-14,实为 CE)。其中 F-5(center-sharing 表述错误)已连同 F-1 修正。

*本节修改:FACTS.md §10.1(richter2025basel 条目)、references.bib(richter2025basel 作者补全)、sections/02_related_work.tex(DORN 句,经 Gate 1 认可措辞)、sections/04_results.tex 与 tables/table1_cohort.tex(center-sharing 事实修正)、本审计文件、GATE1_CODEX_REVIEW.md(新建)。未修改冻结实验产物;未运行 git;未访问 test。*
