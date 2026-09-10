# AE_COR_v2 formal output schema

每个任务目录固定为 `seed_2026/<arm>/`：

- `task.json`：任务、数据指纹和不可变身份。
- `initialization.json`：所有初始 state tensor 的 shape、dtype 与 SHA-256。
- `history.csv`、`tensorboard/`：120 轮完整训练/评测历史和七层实时面板。
- `val_epochs/epoch_001..120/`：compact `predictions_compact.csv.gz` 与完整 `metrics.json`。
- `checkpoints/best.pt`：model-only、selected epoch/metrics/key。
- `checkpoints/last.pt`：model、optimizer、scheduler、AMP scaler、RNG、epoch、history 与当前 best 状态。
- 除上述两个文件外，任务目录内不允许存在其他 `.pt`。
- `best/val`、`last/val`、`best/test`、`last/test`：完整逐图预测、完整 metrics；D/E 另含 `lesion_attention_float16.npz`。
- `RUN_COMPLETE.json`：best/last checkpoint SHA-256、best epoch 和四套最终 metrics。

compact 预测保留所有论文绘图所需的 ID、true/pred score、F0–F3 概率、可用辅助输出和 gate/weak-box 标量。完整预测另含 36 logits、position logits 和 32×32 attention。由此可重画 ROC/PR、校准、混淆矩阵、错误分布、患者聚合、中心分析和 auxiliary 行为图。

实验根目录保存：

- `round_snapshot/`：五项任务唯一可执行源码、配置、环境、runtime 选择和数据指纹。
- `preflight/`：协议验证、全量几何统计/分布图、runtime benchmark 和 A–E smoke。
- `QUEUE_STATE.json`：当前 arm、已完成项、UTC 更新时间、失败类型与文本。
- `SEED_2026_GATE.json`：A–E 机器完整性放行报告。
- `final_ranking/`：单 seed best-test 排名、完整 best/last test 长表、预注册 contrasts 与 10,000 次 paired bootstrap。
- `paper_plot_packs/`：每个 arm 的 best-test ROC、PR、校准、混淆矩阵、患者/中心结果、误差表和总览图。
- `watchdog/`：45 分钟监控的状态证据；不承担最终实验审计 verdict。

预计单任务仅长期保留两个 checkpoint；主要存储来自 120 轮 compact val 和 best/last 四套完整 prediction bundle。旧 `SFibAI-B_AE_COR_v1_1` 目录保持只读历史，不纳入 v2 输出。
