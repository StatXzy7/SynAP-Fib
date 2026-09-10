# 论文入口

- 中文：`zh/main.tex`；英文：`en/main.tex`；补充材料：`en/supplementary.tex`。
- 中英文共享 `en/figures/` 和 `en/references.bib`。中文图注、章节与表格保持独立。
- 原稿内容原样导入，仅中文主文件的共享资源路径改为 `../en/`。
- 英文目录保留事实表、决策和审查笔记，作为写作上下文随本仓库公开，不作为新增验证结论。

从仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_paper.ps1
```

需要已安装 TeX Live、IEEEtran、ctex、latexmk、XeLaTeX、pdfLaTeX 和 BibTeX。PDF 输出为 `paper/zh/main.pdf`、`paper/en/main.pdf` 与 `paper/en/supplementary.pdf`；本地编译文件不提交，图源 PDF 正常提交。

`en/figures/make_*.py` 及 `en/scripts/` 保留原生成脚本。部分脚本依赖原工作区绝对路径或目录层级和未纳入 Git 的受控数据，迁移后不能直接假定可运行。重新生成数据相关图表前须明确外部数据路径及冻结 round，不能因路径整理而触发实验或更换结果。编译已有论文不需要这些数据。
