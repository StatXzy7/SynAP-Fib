# SFibAI-B 正式实验规则

## 权威性与活跃范围

- 当前用户明确指令优先于本文件；本文件优先于仓库内其他说明。
- 本仓库唯一活跃协议是 `AE_COR_v2`。`AE_COR_v1_1` 只由旧 round snapshot 保存，任何活跃脚本、配置或文档不得调用它。
- 所有文本使用 UTF-8，默认不带 BOM。

## 唯一数据协议

- 唯一正式数据集是 Data V4 原生 `train/val/test`：`D:/PhD/liver-Fibrosis-B/data/processed/schisto_2024_clean_v4/manifests/images.csv`。
- train：83,722 images / 4,906 patients / 35 centers；val：20,880 / 1,227 / 33；test：4,107 / 240 / 4。
- 只允许 `train` 反向传播；每轮完整 `val` 负责 checkpoint 选择；冻结后在 `test` 上评测 best 和 last，正式排名只使用 best。
- test 可以重复查看和重跑，不记录访问次数或标签。不得在 test 上反向传播、选择本任务 epoch/checkpoint 或拟合阈值。

## A–E 单 seed 消融

- A：stretch-512，原 SFibAI grading，无 position/lesion。
- B：letterbox-512，原 SFibAI grading，无 position/lesion。
- C：stretch-512 + position。
- D：stretch-512 + weak-box lesion。
- E：stretch-512 + position + weak-box lesion。
- 未启用分支必须真实删除。所有模型从 torchvision `ResNet50_Weights.IMAGENET1K_V2` 重新训练；同 seed 共享 tensor 严格同初始化。
- position posterior 和 lesion attention 均以 detached gated residual 注入 grading；辅助损失与 grading 保持双向 detached 边界。E 叠加两个 residual。

## 训练与 best 选择

- 仅 seed 2026，A→B→C→D→E 单 GPU 顺序训练；每项完整 120 epochs，不 early stop。
- AdamW(lr=1e-4, weight_decay=1e-4)，batch 24，AMP，`StepLR(15, 0.6)`，不按总轮数重缩放。
- position/weak-box 外层权重 0.1；weak-box inside/outside 1.0/1.0，inside pool temperature 10.0。
- 固定 `gate_max=0.5`、`residual_init_scale=0.001`。样本顺序和增强由 `(seed, epoch, image_uid)` 共享。
- epoch 1–20 为 burn-in，永远不具备 best 资格。仅在 epoch 21–120 中依次按更低 val `R_final`、更低 image COR、更早 epoch 选择 best。
- 正式任务全程严格只有 `best.pt`（model-only）和 `last.pt`（完整恢复状态）两个 checkpoint。

## 评测、存储与运行

- COR 只用于评测、best 选择和排名，不进入训练 loss；详细定义见 `EVALUATION_POLICY.md`。
- 推理后只运行一次 canonical evaluator；取消自动 CPU 参考复算和独立 prediction-to-metric 复算，只做唯一 ID、有限值、计数与结构完整性检查。
- 每轮保存完整 val 指标、紧凑逐图预测、history 与七层 TensorBoard；best/last 的 val/test 保存完整逐图预测与全部指标。
- D/E 完整 bundle 保存 32×32 float16 lesion attention。系统性图像/box/mask 几何错位 hard-fail；1 像素或 1 attention cell 边界离散差只 warning。
- 正式产物位于仓库外 `research-private/experiments/SFibAI-B_AE_COR_v2`。旧 `SFibAI-B_AE_COR_v1_1` 不得覆盖或修改。
- 本地 RTX 5090D 先实测 workers 与 eager/compile，选择最快且有效的后端。正式队列只做一次启动前 preflight，随后自动 A→E；普通中断最多一次严格 resume，真实科学数值错误 fail-fast。
- watchdog 每 45 分钟检查队列、进程、日志、产物更新时间和 GPU。代码/工程故障可自动诊断、测试、修复和重新上线；任何会改变科学数值的修复必须停止并报告。

## 结果边界

- 本轮是严格的单 seed 完整比较。可以报告 A–E 的 test 观测排名与 center-stratified patient-cluster paired bootstrap，不得写成多 seed 稳定性或跨总体优越性结论。
- 正式报告必须以独立的 `Test set 主结果` 开头，同时报告 image、patient-max、patient-median、center-balanced 指标以及可用的 position/lesion 指标。
