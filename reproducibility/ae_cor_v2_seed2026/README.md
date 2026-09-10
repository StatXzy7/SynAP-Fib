# SFibAI-B AE_COR_v2 formal pipeline

当前论文唯一活跃代码面：Data V4 原生 split、seed 2026 的 A–E 五组真实结构消融、120 epochs、epoch 21–120 raw COR best 选择、best/last 完整 test 与配对 patient-cluster bootstrap。

历史 `AE_COR_v1_1` 由其旧 round snapshot 原样保存；活跃仓库不再提供旧协议入口。新正式产物写入：

`D:/PhD/liver-Fibrosis-B/research-private/experiments/SFibAI-B_AE_COR_v2`

## 正式执行顺序

1. `python scripts/validate_protocol.py`
2. `python scripts/analyze_preprocessing.py`
3. `python scripts/benchmark_runtime.py --output-dir <benchmark-dir>`
4. `python scripts/run_smoke_matrix.py --runtime-selection <runtime_selection.json> --output-dir <smoke-dir>`
5. `python scripts/create_round_snapshot.py --runtime-selection <runtime_selection.json>`
6. 从不可变 snapshot 运行 `python <snapshot>/scripts/run_queue.py`

启动后 TensorBoard、状态摘要和 45 分钟 watchdog 自动维护。训练设置见 [正式协议](docs/FORMAL_PROTOCOL.md)，产物见 [输出结构](docs/OUTPUT_SCHEMA.md)。
