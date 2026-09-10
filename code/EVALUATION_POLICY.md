# AE_COR_v2 评测政策

## 分数与基础 COR

36-bin posterior 的连续预测为 `y_hat = sum_k p_k*k/10`（k=0..35）。四级边界固定为 0.5、1.5、2.5，边界值进入较高等级。

令 `e=|y_hat-y|`，`d=|grade(y_hat)-grade(y)|`：

`COR = 0.35*e/3.5 + 0.15*I(e>0.3) + 0.15*I(e>0.5) + 0.25*d/3 + 0.10*I(d>=2)`

所有样本等权，不使用旧 F0/F3 1.5 权重。COR 越低越好，只用于评测、checkpoint 选择和排名。

## 三视角综合风险

- `R_image`：逐图基础 COR 平均。
- `R_patient_max`：每患者 true/pred image score 分别取 max 后的基础 COR。
- `R_center_balanced_patient_max`：每中心先算 patient-max COR，再以该中心患者数平方根加权。

`R_final = 0.4*R_image + 0.4*R_patient_max + 0.2*R_center_balanced_patient_max`

patient-median 与 patient-max 对 true/pred 使用完全对称的聚合。

## checkpoint 选择

- 每个 epoch 完整 val；epoch 1–20 只记录，不参与 best。
- 候选域固定为 epoch 21–120。
- 单一选择顺序：更低 val `R_final` → 更低 val image COR → 更早 epoch。
- 不使用平滑、selector bootstrap、27 组敏感性分析或 early stopping。test 不参与本任务 checkpoint、阈值或校准选择。

## 强制保存指标

- Image、patient-max、patient-median：n、MAE、RMSE、±0.3/±0.5 accuracy、四级 accuracy、macro-F1、F0–F3 recall/support、TMAE、severe error rate、COR 及五项 COR 组件。
- Image 概率指标：macro/per-class AUROC、AUPRC、Brier 与 ECE；缺少有效正负类时写 N/A。
- Center-balanced patient-max：中心/患者数、各中心 COR、平方根加权 COR。
- Position：n、accuracy、macro-F1、CE、六类 recall 与 predicted frequency。
- Lesion：valid box count、inside attention、outside ratio、inside/outside、0.5 Dice/IoU；全部作为 weak-box 描述性指标。
- Gate：mean、SD、P10/P50/P90。未实例化分支写 unavailable/N/A，不补零。

## canonical evaluator 与有效性边界

- 聚合使用 float64；推理可使用 AMP；逐图预测至少 float32。
- 每个推理只调用一次 canonical evaluator，结果同时写入 metrics、history/TensorBoard 或最终汇总。
- 不运行自动 CPU 参考复算，也不从落盘 raw prediction 再独立生成第二套 metrics。最低限度检查包括唯一 image_uid、有限预测、概率和、Data V4 数量、分支字段和产物完整性。

## Test paired bootstrap

正式 contrasts 为 A-B、C-A、D-A、E-A、E-C、E-D。对 best test `R_final` 运行 10,000 次按中心分层的 patient-cluster paired bootstrap；所有 arm 共享患者抽样。报告 observed delta、bootstrap mean/SD、percentile 95% CI 与 candidate 更优概率，但正式 A–E 排名仍由单 seed best-test `R_final` 决定。
