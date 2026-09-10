# AE_COR_v2 正式协议

## 实验矩阵与模型

本轮严格只有 seed 2026 × A–E × 120 epochs。A=stretch baseline，B=letterbox baseline，C=stretch+position，D=stretch+lesion，E=stretch+position+lesion。未启用分支真实删除；所有 arm 从 torchvision ResNet-50 `IMAGENET1K_V2` 起点重新训练，同 seed 共享模块逐 tensor 同初始化。

C/E 用 Data V4 六类 `position_norm` 对所有图像训练 position CE；grading 始终只读预测 posterior。D/E 使用 F>0 且存在 box 的 max-grade union weak target，F0 和缺 box 排除。position posterior 与 lesion attention 均经加权特征、gated residual 注入 grading，双向 detached；E 直接叠加两个 residual。

## 数据、几何与训练

- 唯一数据为 Data V4 原生 train/val/test；标签为 `image_label_max`，输出 36-bin，四级边界 0.5/1.5/2.5。
- 输入 512×512；A/C/D/E stretch，B letterbox；ImageNet normalization。
- train 增强：概率 0.7 的非零 90° 倍数旋转；概率 0.5、范围 0.75–1.25 的 saturation；无 flip/crop。paired arm 的样本顺序和逐样本增强一致。
- box union 先在原 ROI 坐标生成 mask，再与图像同步 resize/rotate；mask 用 nearest。系统性错位 hard-fail，1 像素/1 attention cell 边界离散差 warning。
- 原 SFibAI hybrid grading loss：alpha=1.0、beta=0.02、gamma=0.02、soft_label_std=1.0。position 与 weak-box 外层权重各 0.1；inside/outside 1.0/1.0；inside pool temperature 10.0。
- AdamW(lr=1e-4, weight_decay=1e-4)，batch 24，AMP，`StepLR(step_size=15,gamma=0.6)`，120 epochs，不 early stop。

## 评测、best 与存储

每轮完整 val；epoch 1–20 为 burn-in，不具备 best 资格。仅在 21–120 中按 raw val `R_final`、image COR、earlier epoch 选择 best。取消平滑、selector/bootstrap 和 27 组敏感性分析，仅保留完整选择轨迹。

每轮保存 compact predictions、完整 metrics/history/TensorBoard。TensorBoard 固定七层：Image accuracy、Patient accuracy、COR selection、AUC/calibration、error profile、auxiliary、training health。Image accuracy 位于首页第一组，Patient accuracy 第二组。

全程严格只有两个 checkpoint：best model-only 与滚动 last full-state。训练结束后自动生成 best/last 的完整 val/test；正式排名只使用 best test。每个推理只运行一次 canonical evaluator，不进行 CPU 参考或落盘预测独立复算。

## preflight、队列和恢复

启动前一次性完成：Data V4 指纹/计数、全量宽高比与 letterbox padding 分布、A–E 几何/结构 smoke、两个 checkpoint 合同、workers 4/6/8 与 eager/compile GPU 基准。选择实测最快且有效的后端后创建不可变 source/environment/data/runtime snapshot。

本地 RTX 5090D 按 A→B→C→D→E 自动顺序运行。普通外部中断最多自动 strict resume 一次；配置、数据、非有限数值、评测或审计错误 fail-fast。45 分钟 watchdog 负责检查控制器/训练进程、产物与日志更新时间、GPU，并可在不改变科学数值时自动修复工程 bug、测试和重新上线。

## 完成收尾

五项全部通过机器完整性 gate 后，自动运行固定 contrasts 的 10,000 次 center-stratified patient-cluster paired bootstrap，生成选择轨迹、paper/reviewer pack、test-first 排名和状态摘要。正式实验全部结束后再运行一次 verdict-bearing experiment audit；不得把每次 watchdog 轮询当成正式审计。
