# AE_COR_v2 最终排名标准

## 唯一排名规则

- 仅比较同一不可变 snapshot 下 seed 2026 的 A–E 五组完整结果。
- 各 arm 必须先完成 120 epochs，并由 epoch 21–120 的 val `R_final` 选出 best。
- 正式排序按 best checkpoint 的 test `R_final` 升序；完全相同时按 test image COR、arm 名称排序。last test 只作等 epoch 诊断，不改变排名。
- 本轮不计算或伪造多 seed mean±SD，也不使用 margin、方向门、TIE 或 superiority 标签改变观测排名。

## 配对报告

- 固定 contrasts：A-B、C-A、D-A、E-A、E-C、E-D。
- delta 固定为 candidate-reference；负值表示 candidate 风险更低。
- 每个 contrast 报告 10,000 次 center-stratified patient-cluster paired bootstrap 的 observed delta、mean、sample SD、95% percentile CI 与 `P(candidate better)`。

## 报告顺序与结论边界

- 报告首先给出独立醒目的 `Test set 主结果`，包含 best 排名、last 对照、best epoch、checkpoint SHA-256、image/patient-max/patient-median/center-balanced 全指标及辅助分支指标。
- validation 只解释 checkpoint 来源、burn-in 排除、训练轨迹与机制证据。
- 结果表述限于“Data V4、seed 2026 的观测排名”。长程训练不能替代多 seed 统计，本轮不得写成跨初始化稳定性或外部泛化优越性。
