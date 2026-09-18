# SynAP-Fib ICLR 2027

这个目录是 SynAP-Fib 的 ICLR 2027 投稿工作区，用于集中维护论文源文件、审计记录、实验边界和可复现脚本。它与工作区中的历史 TMI 版本分开，后续论文更新优先在这里进行，再按需要回写其他内部材料。

## 当前状态

- 当前内容是 ICLR-oriented draft，尚未达到可提交状态。
- 当前稿件明确把结果解释为 task-specific anatomical concept pathway 的证据；尚未完成 direct concept intervention，因此不宣称 faithful 或 causal explanation。
- 正式结果必须遵守项目的 `train -> val 选择 checkpoint -> 冻结 -> test 比较` 协议。面向用户的结果报告必须先给出独立的 **Test set 主结果**，并同时报告 patient-level 与 image-level 指标。
- 论文源文件可公开同步；临床图像、原始数据、模型 checkpoint、运行日志和生成 PDF 不放入此目录。

## 目录结构

- `main.tex`：当前 ICLR 稿件入口。
- `main_iclr.tex`：兼容性的 ICLR 入口；日常编辑以 `main.tex` 为准。
- `supplementary.tex`：补充材料入口。
- `sections/`、`tables/`、`figures/`：论文正文、表格、图形源文件和主稿实际引用的 PDF 图像。
- `FACTS.md`、`DECISIONS.md`、`ICLR_REWRITE_PLAN.md`：事实边界、决策记录和投稿计划。
- `P1_*`、`P2_*`、`P3_*`、`GATE*_*.md`、`SELF_AUDIT.md`：审计与生产记录。
- `scripts/`：引用、元数据和图表辅助脚本。

## 本地更新流程

1. 在本目录修改 LaTeX、计划或审计文件。
2. 需要生成 PDF 时，把生成物放在本地临时目录；不要提交 PDF、日志、aux 文件或临床图像。
3. 运行仓库测试和适用的论文审计后，提交 `paper/iclr2027/` 下的明确文件。
4. 推送到 `SFibAI-B` 的 `main`，其他机器用 `git pull` 同步。

当前 ICLR 官方样式文件已作为源文件保留；如果会议发布新版本，应在此目录单独更新并记录版本来源。

## 与其他论文目录的关系

`paper/iclr2027/main.tex` 是当前新的 ICLR 版本；`paper/en/main.tex` 是原先的英文论文目录，保留作既有版本和共享资源来源，不是 ICLR 主稿入口。
