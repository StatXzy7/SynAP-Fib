# 来源与迁移记录

导入日期：2026-09-10。源目录原位保留，新仓库不携带旧仓库的全部历史，避免将历史数据、缓存或不相关文件一并发布。旧历史继续保存在原仓库。

| 新目录 | 原来源 | 身份 |
| --- | --- | --- |
| `code/` | `SFibAI-B/` 的 Git 跟踪文件 | `14640b3c99f1143c3201eec4c30a03dccf333a60`，导入时工作树干净 |
| `reproducibility/ae_cor_v2_seed2026/` | `research-private/experiments/SFibAI-B_AE_COR_v2/round_snapshot/` | snapshot 记录 git head `2acac9173e51f8b6cfcde104ae9be071668feb63` |
| `paper/zh/` | `paper-plan/05_manuscript/synap_fib_tmi_20260904_zh/` | 当前中文稿 |
| `paper/en/` | `paper-plan/05_manuscript/synap_fib_tmi_20260904/` | 英文稿、补充材料、共享图片与文献 |

源路径均相对于原工作区 `D:/PhD/liver-Fibrosis-B`。逐文件来源及 SHA-256 见 [IMPORT_MANIFEST.json](IMPORT_MANIFEST.json)。该表是导入时基线，不随日常编辑改写。中文主文件只调整共享资源路径；中文 README 更新导航。

冻结快照的 66 个清单文件在复制前逐一核对原 snapshot SHA-256，全部一致；原 snapshot_manifest.json 原样保留。后续自动检查持续校验该冻结副本。

当前 `code/README.md` 与部分规则文档仍含历史轮次描述，已原样保留。实际导入代码 `src/sfibai_b/protocol.py` 和配置是 lambda A/E/G 轮。论文复现应查阅单独保存的原轮快照，不混用这两个配置。

代码尚保留原 Windows/HPC 路径和原 Python 包名；目录迁移验证不等同于在任意新机器上通过训练复现。图表生成同样需要受控的外部结果文件。此仓库提供来源可追溯的代码与可独立编译的稿件。

新仓库最初按私有范围准备；项目负责人于 2026-09-10 明确选择公开上传当前整理内容，仓库为 Public。原始数据、患者清单、逐图预测、权重、运行日志、临时页图、候选病例筛选表和旧 Git 历史未导入。论文实际使用的定稿图源以及写作事实、决策与审查笔记保留。

Git 使用 `.gitattributes` 保留原文件字节和换行符，以便 Windows/Linux 间克隆仍可通过冻结 SHA-256 校验。原有 CRLF 和文件末尾空行予以保留；新增说明文件使用 UTF-8 无 BOM 与 LF。
