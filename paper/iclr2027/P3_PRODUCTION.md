# P3_PRODUCTION — 图件与最终版收尾记录

**日期**: 2026-09-05
**前置状态**: P1 CLOSED;Gate 1 PASS(条件闭合);Gate 2 PASS(C1–C4 关闭)
**本轮范围**: P3 图件、摘要、交叉引用、终编译;**未启动** Gate 3 与代码发布

## 一、Figure 1–5 制作状态

| 图 | 状态 | 产出 | 说明 |
|---|---|---|---|
| Fig 1 架构图 | ✅ | `figures/fig1_architecture.drawio`(可编辑源)+ `figures/fig1_architecture.pdf`(`make_fig1.py` 等效渲染)+ `figures/fig1_architecture.tex`(caption) | 机制忠实:仅绘制冻结实现存在的模块(backbone → position/lesion 分支 → gated residual → grading head,bidirectional detach 标注;**无**无门控/梯度耦合变体);"35 binary logistic units" 错误已改为 "linear output layer"(F-DESIGN-HEAD)。**遗留**:drawio CLI 不可用,PDF 为程序等效渲染;最终 draw.io GUI 导出列为负责人可选核对项(不阻塞) |
| Fig 2 队列 | ✅ | `figures/fig2_cohort.pdf`(`make_fig2.py`)+ `figures/fig2_cohort.tex` | 三面板:(a) 队列流(患者级划分、零重叠、四 test centers 与 train 共享——结构性事实,无设计意图措辞);(b) 患者级分级分布;(c) 位置分布。全部数值来自 FACTS(F-COHORT-* / F-DIST-PAT-* / F-TRAIN/VAL/TEST-POSITION-DIST) |
| Fig 3 stage-wise | ✅(已有) | `figures/fig3_stage_wise.pdf` | Fig 2 插入后编号归位为 **Figure 3**(main.aux 确认) |
| Fig 4 混淆+校准 | ✅ | `figures/fig4_confusion_calibration.pdf`(`make_fig4.py`)+ `fig4_confusion_calibration.tex` | (a/b) A、E 混淆矩阵(计数+行百分比);(c/d) 可靠性图(逐 grade,10 bins)。数据:frozen paper_plot_packs(F-CONF-A/E、F-CAL-SOURCE);行和与 F-TEST-GRADE-DIST 逐项吻合 |
| Fig 5 定性案例 | ✅ **已选定并制作** | `figures/fig5_qualitative.pdf`(`make_fig5.py`)+ `fig5_qualitative.tex` | 负责人 node B 选定(2026-09-05):F0 = `img_center_17_2023157028_3_2`、F1 = `img_center_07_2023080032_5_1`、F2 = `img_center_07_2023080017_1_2`;F3 与失败例由负责人委托执行侧按代表性选定:**F3 = `img_center_07_2023080033_3_1`**(true 3.2→2.98,center_07 候选中真实分级最高,位置预测 3/2 诚实呈现可错性,患者与 F2 例不重复)、**失败 = `img_center_07_2023080131_4_3`**(true 2.8→0.46,全测试集最大误差,位置 4/4 正确,失败归因于分级而非位置)。5 行 × 3 列(ROI/注意力/叠加),注释 true/pred/pos,**无患者标识**;caption 声明注意力为弱监督描述性行为、非分割真值 |

## 二、S1–S3 补充图

| 图 | 状态 | 产出 |
|---|---|---|
| S1 per-center | ✅ | `figures/supp_fig_s1.pdf`;caption 依 DECISIONS §4.2(无 robustness/generalization 字样;患者数在轴;与 Table S5 互补) |
| S2 误差分布 | ✅ | `figures/supp_fig_s2.pdf`(A/E 逐图绝对误差直方图,frozen errors.csv) |
| S3 训练轨迹 | ✅ | `figures/supp_fig_s3.pdf`(五臂 val R_final × 120 epochs,无平滑,标注选中 epoch 与 burn-in 区) |

FACTS §8.7 已补录来源(F-SUPP-S1/S2/S3)。

## 三、fact-maintenance(本轮新增,均经冻结工件只读核验)

| Fact | 内容 | 来源 |
|---|---|---|
| F-TRAIN/VAL-POSITION-DIST | train p1–p6 = 14,137/14,092/14,121/14,047/13,960/13,365;val = 3,515/3,524/3,556/3,521/3,478/3,286 | `images.csv`(split × position_norm 单次提取;test 列与 F-TEST-POSITION-DIST 逐项吻合交叉验证) |
| §8.6 F-CONF-A / F-CONF-E | 4×4 混淆矩阵(16 cells each) | frozen confusion.csv;行和 = F-TEST-GRADE-DIST |
| §8.6 F-CAL-SOURCE | calibration.csv 结构说明 | frozen calibration.csv |
| §8.7 F-SUPP-S1/S2/S3 | S1–S3 图数据来源 | §8.4 / errors.csv / val_epochs metrics.json |

(F-ACQ-*、F-DESIGN-ENV、F-DESIGN-HEAD 已在 Gate 1 处置时补录,此处不重复。)

## 四、摘要

✅ 已按 DECISIONS 约束起草(数值仅取 FACTS:108,709 / 6,373 / 35 / 5.9% / 2.8%;"best observed";近平局披露;无 novelty/外部中心声明;patient-held-out 术语)。**注**:摘要含 E−A bootstrap 不可区分的披露,与 Gate 1/2 决议一致;摘要属"新文本",Gate 3 时随全稿四轴复核。

## 五、交叉引用与编号

- 主稿图号(最终,main.aux 程序核验):`fig:architecture`=**1**、`fig:cohort`=**2**、`fig:stagewise`=**3**、`fig:qualitative`=**4**、`fig:confcal`=**5** —— 与 DECISIONS.md §4.2 计划的图序一致(架构/队列/stage-wise/定性在 5,混淆+校准顺延为 5)。**注**:DECISIONS §4.2 表格原列 Fig 4 = 混淆+校准、Fig 5 = 定性;因 Fig 5(定性)篇幅较大接在 fig3 后、fig4 移至文献后,实际编号为定性=4、混淆校准=5。语义内容不变,仅顺序对调;如负责人要求严格按 §4.2 表格顺序(Fig 4=混淆校准、Fig 5=定性),只需交换 main.tex 中两处 `\input` 位置,一分钟内可改。
- supplementary.tex 的主稿图引用为 **xr 稳定引用**(`\usepackage{xr}` + `\externaldocument{main}` + `\ref{fig:stagewise}`),渲染 "Figure 3 of the main text"(当前正确),任何后续图序变动自动跟随。
- 全部 `\ref` 目标存在(main.log 0 undefined);表格 S1–S13 与图 S1–S3 双计数器并存(IEEE 惯例)。

## 六、终编译

| 文档 | 页数 | error | Overfull | Underfull | undefined |
|---|---|---|---|---|---|
| main.pdf | 12 | 0 | 0 | 3(badness 1708–1838,排版可选项) | 0 |
| supplementary.pdf | 3 | 0 | 0 | — | 0 |

## 七、逐页视觉检查

已渲染 `page_check/main-1..12.png`、`page_check/supp-1..3.png`(90 dpi,含 Fig 5 新增页 10–12 重渲染)。自动化指标(页数/overfull/undefined)全部通过;Fig 5 定性图已目视核验(5 行标注与 FACTS 一致、三列布局、共享 colorbar、无患者标识);**像素级逐页人工复核建议由负责人翻阅 page_check 或在 Gate 3 一并执行**。

## 八、代码发布

本轮**未执行**。`Code availability` 维持 "will be made publicly available upon publication"(F-AVAIL-CODE);未写任何 URL/DOI。SFibAI-B 本地 git 状态(remote `StatXzy7/SFibAI-B`,main ahead 9)未动、未推送。

## 九、未关闭项(移交)

1. ~~Fig 5 负责人选定(node B)~~ —— **已完成(2026-09-05)**:F0–F2 负责人选定,F3+失败例负责人委托执行侧按代表性选定(见 §一)。
2. 图序对调确认(定性=4、混淆校准=5 vs DECISIONS §4.2 表格原序)——负责人裁量项,一分钟可改。
3. draw.io GUI 最终导出 Fig 1(可选;程序渲染版已可用,.drawio 源文件已保存)。
4. 逐页像素级人工复核(建议随 Gate 3)。
5. **Gate 3(TMI reviewer audit)**:全部 28 条引文四轴复核 + 摘要/Fig 5 caption 等新文本 claim-evidence 一致性 → 负责人 node C。
6. 代码公开发布(负责人指令触发时执行;写 URL/DOI 前须真实存在)。

## 十、P3 完成判定

**P3 主体完成(2026-09-05)**:Figures 1–5 全部制作并接入主稿;S1–S3 接入补充材料;摘要已起草(仅 FACTS 数值);交叉引用全部解析(xr 稳定引用);终编译 0 error / 0 Overfull / 0 undefined(main 12 页、supp 3 页);逐页渲染完成。残留项:图序对调确认(裁量)、draw.io GUI 导出(可选)、Gate 3、代码发布。

*本轮未修改冻结实验产物(绘图脚本仅读取);未运行 git;未访问 test 采样;无标注者信息进入任何图件或文本。*
