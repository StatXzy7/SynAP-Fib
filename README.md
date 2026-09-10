# SynAP-Fib

协同解剖先验驱动的超声肝纤维化细粒度分级。论文与代码统一维护仓库。

本仓库按项目负责人于 2026-09-10 的决定公开维护：[StatXzy7/SynAP-Fib](https://github.com/StatXzy7/SynAP-Fib)。尚未声明开源许可证。项目名沿用论文方法名 SynAP-Fib，不绑定投稿期刊、日期或内部实验代号。

| 入口 | 用途 |
| --- | --- |
| [中文论文](paper/zh/main.tex) | 当前中文修改入口 |
| [英文论文](paper/en/main.tex) | 英文主稿；现有稿件声明以英文为准 |
| [补充材料](paper/en/supplementary.tex) | 英文补充材料 |
| [参考文献](paper/en/references.bib) | 中英文共用文献库 |
| [论文编译说明](paper/README.md) | 编译和图片维护 |
| [当前代码](code/) | 导入时为 AE_COR_v2_seed2026_lambda，A/E/G |
| [论文冻结代码](reproducibility/ae_cor_v2_seed2026/) | 论文原始 seed 2026 结果所对应的 AE_COR_v2 快照 |
| [来源与迁移说明](docs/PROVENANCE.md) | 版本关系、校验和环境限制 |
| [日常维护](CONTRIBUTING.md) | 修改、检查、提交与推送 |

当前开发代码与论文结果快照是两个不同版本，不能用当前代码版本号为历史论文结果背书。源码保持原 Python 包名 `sfibai_b`，以保留导入兼容性。

本仓库保存论文所用图片与汇总表，不包含原始数据、逐图预测、患者清单、模型权重和训练产物。模型训练仍需原受控数据和对应环境；本次整理不运行实验或重新计算结果。
