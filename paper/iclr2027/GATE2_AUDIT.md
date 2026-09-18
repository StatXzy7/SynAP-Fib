# GATE2_AUDIT — Codex Gate 2 审计记录(四轴引文审计 + 术语/overclaim)

**日期**: 2026-09-05
**审查方**: Codex(MCP,thread `01a07112-ef0b-7363-a1e6-c6098f70a6c4` 延续,round 3)
**被审对象**: Gate 1 PASS-WITH-CONDITIONS 后的稿件(28 条引文全部 + 本轮三项修订)
**前置状态**: Gate 1 = PASS-WITH-CONDITIONS(2026-09-05);本轮处置其条件 1、2
**执行方**: Claude Code(ZCode 侧);审查侧 Codex,跨模型独立性成立

## 一、执行侧 Gate 2 准备(提交审查前完成)

### 1.1 轴 1/2:存在性与元数据审计(脚本化,2026-09-05)

工具:`scripts/gate2_metadata_audit.py`(新建)。对 `references.bib` 全部 28 条逐项与 Crossref API 对照:**DOI 解析、题名、年份、卷、期、页码/文章号** 六项。

| 结果 | 数量 | 明细 |
|---|---|---|
| 26 条含 DOI | **26/26 全部 OK** | 题名/年份/卷/期/页码与 Crossref 完全一致,零失配 |
| 2 条无 DOI(中文标准/手册) | 手工核验 | `moh2006schistocriteria`(WS 261–2006):URL 实测 HTTP 200,`application/pdf`,2,765,523 字节;`moh2000schistomanual`(第 3 版手册):与已发表前作(Nature Communications 终版 References.bib 第 464 行)逐字一致,DECISIONS.md §8 明确允许无 DOI 的官方指南条目 |

注意点:`dorn2018` 为 inproceedings(CVPR,页码 2002–2011,Crossref 一致);`xu2026sfibai` 卷期未分配(early cite,符合 DECISIONS.md §8 "不得虚构卷期")。

### 1.2 轴 3:句级支持审计(28/28,基于摘要快照 + 本会话补采)

方法:`scripts/citecontext.py` 提取当前稿件全部 29 处 `\cite` 语境(28 个唯一 key),逐条对照 `tables/cited_abstracts.json`(26 条摘要快照)+ 本会话补采的 zhou2020mtlabus(Semantic Scholar)与 shamtl2021(Springer)摘要。逐条判定见第三节表格。

### 1.3 轴 4:转述强度审计

逐句检查相关工作的结论是否被表述得强于原文(DECISIONS.md Gate 3 四轴之第四轴提前执行)。重点复核 Gate 1 修改过的三处 + SHA-MTL 新句。

### 1.4 本轮执行的三项修订

| # | 修订 | 内容 |
|---|---|---|
| R1 | Positioning 有界观察(Gate 1 条件 2) | "Prior work generally reports a single auxiliary signal in its favourable configuration." → **"Several of the closely related studies considered here use a single auxiliary signal in their favourable configuration."**(负责人指令措辞;自指本节已审文献,自我支撑,不再是无界文献概括) |
| R2 | supplementary Figure~3 硬编码(提前处置) | `supplementary.tex` "Figure~3 of the main text" → `\usepackage{xr}` + `\externaldocument{main}` + `Figure~\ref{fig:stagewise} of the main text`。**稳定引用**:自动追踪主稿图号(现解析为 Figure 2,P3 插入队列图后自动变 3)。实测:supplementary.pdf 渲染 "Figure 2 of the main text",无 undefined 引用;S8 标题中 Table~IV 亦正确解析 |
| R3 | 重编译验证 | main.pdf 9 页 / 0 error / 0 Overfull;supplementary.pdf 3 页 / 0 error / 0 Overfull;xr 跨文档解析正常 |

## 二、四轴逐条审计表(28/28)

证据基础:`tables/cited_abstracts.json` 摘要快照(26 条)+ 本会话补采 zhou2020mtlabus、shamtl2021 摘要 + xu2026sfibai 前作全文(P1/P2 核验)+ 旧稿 Data Collection 正文。轴 3 判定:✅ = 摘要/全文直接支持该句;⚠️ = 支持为间接/语境级,已标记请 Codex 裁量。

### A. 临床/数据集组(10)

| Key | 引用语境(现稿) | 摘要证据 | 轴3 支持 | 轴4 转述强度 |
|---|---|---|---|---|
| schistoelasto2018 | 流行区 TE/MRI 少有;血吸虫表型异于其他病因 | pSWE 评估 mansoni PPF,"few studies in schistosomiasis mansoni" | ✅(语境级) | ✅ 无增强 |
| schistopocus2024 | (同上共引) | 血吸虫超声分期系统 scoping review(192 研究,Niamey/Cairo 演变) | ✅ | ✅ |
| interobserver2019 | "interobserver agreement is a recognized concern" | 研究 SWE 分期观察者间一致性;**其自身结论为 excellent(ICC 0.92)** | ⚠️ **标记**:该研究存在本身支持"recognized"(领域在测量它),但该文结论为阳性——引用方向存在张力,请 Codex 裁量 | ⚠️ |
| swe2018staging | "diagnostic accuracy varies across devices and acquisition settings" | 2D-SWE 分期 meta 分析,汇总敏感度/特异度跨研究异质 | ⚠️ **标记**:摘要支持"跨研究汇总",但"varies across devices and acquisition settings"为具体归因,摘要未明示设备级变异,请 Codex 裁量 | ⚠️ |
| usfibrosisgan2022 | 生成式增强补偿有限数据 | "A data augmentation method based on a GAN model was used" | ✅ | ✅ |
| microflow2023 | 造影微流 cines 输入 | 题名:integration of contrast-enhanced micro-flow cines, B-mode, clinical parameters | ✅(题名级,描述性) | ✅ |
| hfus2025 | 高频采集暴露细微纹理 | 高/低频配对比较,HF 优 | ✅ | ✅ |
| liverspleen2025 | 配对器官视角 | 题名:Paired liver–spleen network | ✅(题名级) | ✅ |
| richter2025basel | 中国分级与国际指南对应关系在 Basel 协议中描述 | WHO 专家会议建立亚洲血吸虫标准化协议;Niamey 未覆盖 japonicum 特异性;旧稿正文明确该对应关系在 Basel 协议论述 | ✅ | ✅ |
| xu2026sfibai | 36 级 posterior + 期望;江苏入组标准;SFibAI 架构 | 前作全文:multicentre 36-level;期望表述见正文 Methods;入组标准见 Data Collection(P1/P2 逐行核验) | ✅ | ✅(仅方法归属,无性能对比) |

### B. 序数方法组(6)

| Key | 引用语境 | 摘要证据 | 轴3 | 轴4 |
|---|---|---|---|---|
| coral2020 | 架构式 rank consistency | weight-sharing constraint → rank-monotonicity 保证 | ✅ | ✅ |
| corn2023 | 条件概率分解 | conditional training sets → chain rule → unconditional rank probabilities | ✅ | ✅ |
| dorn2018 | 离散化 + per-bin 概率分布(Gate 1 修正后措辞) | SID 离散化 + ordinal regression(全文 Eq.5 核验:阈值+中点解码,现句未再归因解码方式) | ✅ | ✅ |
| unimodalbeta2021 | unimodal 正则 | beta-distribution unimodal regularisation | ✅ | ✅ |
| sonnet2022 | 分级+分割联合 | SONNET 核分割+分类,ordinal | ✅ | ✅ |
| drgraduate2020 | 不确定性感知视网膜分级 | uncertainty-aware DR grading | ✅ | ✅ |

### C. 解剖先验/多任务组(9)

| Key | 引用语境 | 摘要证据 | 轴3 | 轴4 |
|---|---|---|---|---|
| attentiongated2019 | 无显式定位监督的注意力 | "eliminate the necessity of using explicit external tissue/organ localisation modules" | ✅(强匹配) | ✅ |
| anatomyxnet2022 | 解剖分割掩码监督注意力 | organ-level annotations → anatomy-aware attention,胸部疾病分类 | ✅ | ✅ |
| agmbtransformer2021 | 解剖定义分支路由,根管治疗评估 | anatomy-guided multi-branch Transformer for root canal therapy(P2 修正后归因) | ✅ | ✅ |
| opticdisc2020 | 杯盘包含关系引导 | anatomical knowledge guides segmentation;cup-to-disc ratio | ✅ | ✅ |
| hovertrans2023 | 水平/垂直组织分层入注意力结构 | inter-/intra-layer horizontal+vertical,BUS transformer | ✅ | ✅ |
| zhou2020mtlabus | joint learning improves outcomes of both tasks(D2 修正后措辞) | "learning these two tasks jointly is able to improve the outcomes of both tasks"(S2 补采摘要,逐字匹配) | ✅(强匹配) | ✅ |
| shamtl2021 | (同句共引) | 分割 sens/DICE +2.27%/+1.19%,分类 acc/F1 +2.45%/+3.82% vs 单任务 | ✅(强匹配) | ✅ |
| petsnet2023 | 胎脑 pose+分割联合 | "jointly learn the pose estimation parameters...and tissue segmentation...fetal MRI" | ✅ | ✅ |
| covidweak2020 / weakbreast3d2019 | 图像级监督的弱定位,取得相关效果 | weakly-supervised lesion localization, image-level labels(两篇摘要均明示) | ✅ | ✅ |

### D. 标准类(3 计入,与前述 10+6+9 合计 28;zhou/shamtl 已计入 C)

| Key | 引用语境 | 证据 | 轴3 | 轴4 |
|---|---|---|---|---|
| moh2000schistomanual | 四级分级源自中国国家级分级系统 | 前作同条目、同用法;负责人 P1 答复 D 确认 | ✅ | ✅ |
| moh2006schistocriteria | (同句共引) | 同上;URL 存活核验(HTTP 200) | ✅ | ✅ |

### 执行侧汇总

- 轴 1(存在性):28/28 ✅(26 DOI 解析 + 2 手工);
- 轴 2(元数据):26/26 Crossref 全项一致,0 失配;xu2026sfibai 卷期未分配属预期;
- 轴 3(句级支持):26/28 ✅,**2 项 ⚠️ 标记**(interobserver2019、swe2018staging,见上表)待 Codex 裁量;
- 轴 4(转述强度):26/28 ✅,2 项随轴 3 标记;SHA-MTL/zhou/DORN 三处 Gate 1 修改后措辞均为证据匹配表述。

## 三、Codex Gate 2 审查结果(2026-09-05,同线程 round 3)

### 判定

> **PASS-WITH-CONDITIONS** — R1 resolves the outstanding positioning condition. Both flagged Introduction citations require evidence-matched wording. Two previously unreported issues remain in the unchanged manuscript: an unsupported interpretation of stage-wise errors and a bootstrap proportion outside its permitted location.

Codex 同时确认:Gate 1 条件 2(有界观察)**Resolved**;DORN/SHA-MTL 修改后句子维持关闭("acceptable as a summary of the cited studies' reported comparisons");D3–D5 负责人决定维持关闭;R2(xr 稳定引用)接受。

### 四项条件的处置

| # | Codex 要求 | 处置 | 状态 |
|---|---|---|---|
| C1 | interobserver2019 改写(该文结论为 excellent agreement,原引用方向误导) | ✅ **已执行**,采用 Codex 给出的逐字替换措辞:"Interobserver reproducibility has also been evaluated in shear-wave elastography for hepatitis C-associated liver fibrosis, with excellent agreement reported for the point shear-wave method studied by Kaposi et al.~\cite{interobserver2019}" | 关闭 |
| C2 | swe2018staging 改写(meta 分析支持跨研究异质性 + 设备/方案为 possible contributors,不支持设备级归因)+ 段落级后果("This variability motivates…" 不得暗示 SWE 研究证明自动化解决 B-mode 变异性) | ✅ **已执行**,两处均采用 Codex 逐字替换:"a meta-analysis of two-dimensional shear-wave elastography reported heterogeneity in diagnostic performance across studies, with differences in sampling protocols and equipment discussed as possible contributors" + "These studies concern elastography rather than automated grading of B-mode images. A separate body of work applies deep learning…" | 关闭 |
| C3 | **HIGH — Discussion F1/F2 误差机制推断无证据支持**:"F1 errors tend to cross a grade boundary while remaining small in magnitude, whereas F2 errors are larger in magnitude without necessarily changing the assigned grade" —— FACTS 仅有边际的 stage-wise MAE 与 recall,不能建立误差幅值×跨级联合关系 | ✅ **已执行(2026-09-05,负责人决定:选项 (i) 删除,不追加联合误差分析)**:推断句已删除;保留有证据支持的观察表述 "These two metrics therefore identify different stages as hardest"(即 F2 最大 MAE、F1 最低 recall 的直接读数)与其后已获批的 "clinically plausible" 弱化句;其余措辞不变 | **关闭** |
| C4 | **MEDIUM — 补充材料正文出现 P = 0.533**(DECISIONS.md §4.3 仅允许 P(candidate better) 出现在补充表格注释) | ✅ **已执行**:删去正文 "with $P = 0.533$",保留区间解释;表格注释中的 P 值与其澄清语不变 | 关闭 |

### 附带元数据核验(Codex 提示后执行)

Codex 提示 interobserver2019(Kaposi)在线 2019-08、正式刊 2020-02(JCU 48(2));swe2018staging(Zhang)在线 2018-08、正式刊 2019-03(JUM 38(3))。Crossref 双确认(published-print 2020-2 / 2019-3)。按 P2 惯例(以正式卷期年份为准,与 agmbtransformer2021→2022 等四条修正一致):**两条 bib 年份已更正为 2020 与 2019**,cite key 不变。

### 编译验证(修订后)

main.pdf 9 页 / 0 error / 0 Overfull / 0 undefined(含 bibtex 重跑);supplementary.pdf 3 页 / 0 error / 0 Overfull / 0 undefined。

### Gate 3 待办(Codex 开出)

1. ~~C3(F1/F2 推断)负责人决定后关闭~~ —— **已关闭(2026-09-05,负责人选项 (i))**。
2. 保留完整引文审计链(实际 bib 条目、元数据对照、句-源证据);Codex 注明本次为定向裁量,非对执行方全部 28 条四轴结论的独立认证 —— Gate 3 仍将全面审计引文。
3. 替换架构占位图 + 终稿图件/caption/交叉引用/摘要的 claim-evidence 一致性检查(P3)。
4. 保持 D3–D5 决定范围不扩大(持续约束)。

### Gate 2 状态

**PASS(2026-09-05,C1–C4 全部关闭)**。

- C1(interobserver2019 改写)✅;C2(swe2018staging 改写 + 段落后果句)✅;C3(F1/F2 推断删除,负责人决定 (i))✅;C4(P 值位置)✅;
- 修订后编译:main.pdf 9 页 / 0 error / 0 Overfull / 0 undefined;supplementary.pdf 3 页 / 0 error / 0 Overfull / 0 undefined;
- Gate 1 条件 1(引文四轴审计,执行侧全量 + Codex 定向裁量)与条件 2(有界观察)均关闭;条件 3(Figure 1 draw.io)与条件 4(措辞范围)移交 P3/持续约束。

**工作流状态:P1 CLOSED → Gate 1 PASS-WITH-CONDITIONS(条件已闭合)→ Gate 2 PASS。下一步:P3 图件与最终版收尾(Figure 1–5、S1–S3、摘要、交叉引用、终编译、逐页视觉检查),P3 完成后 Gate 3(TMI reviewer audit)→ 负责人 node C。**

*本记录含执行侧四轴审计(§一、§二)与 Codex 审查结果(§三)。未修改冻结实验产物;未运行 git;未访问 test;未发布代码 URL/DOI。*

