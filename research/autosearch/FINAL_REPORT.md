# Test set 主结果

TEST PENDING / 结果未完成。Test 未执行或产物尚不完整。

预锁定主终点：R_final = 0.4 image COR + 0.4 patient-max COR + 0.2 sqrt(center n) 加权 patient-max COR；越低越好。
本轮固定 seeds: 34001, 34002, 34003。历史 test 已有暴露；本轮搜索阶段隔离 test。

## 开发集结果与 checkpoint 选择

SEARCH_COMPLETE.json: 未完成；无可报告的正式开发排名。
CONFIRM_COMPLETE.json: 未完成；无可报告的正式开发排名。

## 指纹与完成状态

Data audit: PASS; image hashes verified: 108709。
Manifest SHA256: 73a14221ea1a67f3248351a4ed5d08574f904175e69d9129ab2e705a0bb86a40
Annotations SHA256: 6684cb633ad055eb55f399a6383f531b5e8cf4db0a3ef828fb6967c16150d167

## 软件与环境验证

正确 CUDA 环境为 `D:\anaconda3\envs\cv\python.exe`：Python 3.10.20、PyTorch 2.11.0+cu128、CUDA 12.8、RTX 5090 D。两个 editable 包安装完成；CUDA smoke 通过，真实 inner-train batch=8，FP32 与 BF16 loss/gradient 均有限。
隔离包测试 46 passed；关键旧回归测试 15 passed；Python 编译检查通过。

## 实际执行状态

E_reference seed31001 的已有 checkpoint 只完成到 epoch 38，status 文件停在 epoch 39/batch 2300；当前没有活动控制进程。使用 `--resume` 时，代码指纹与 `outputs/execution_snapshot` 完全匹配，但严格环境指纹不匹配：锁定记录为 Windows build 26100，当前为 26200，因此 resume 被拒绝。未修改锁、未强行恢复旧 checkpoint。

未完成：120 epoch E_reference、8+24+8 搜索、三个 seed 确认、FINAL_MANIFEST 冻结、final-test 及统计验收。没有生成可执行的占位 manifest。

## 限制

弱框指标是 weak-box agreement；真实轮廓分割与外部临床效用未独立验证。未完成的训练、确认或 test 均不构成性能提升证据。成本、环境、源代码和数据指纹保存在各 trial identity/result、ENVIRONMENT、DATA_AUDIT 与 ROUND_LOCK 文件。

实时状态：`outputs/controls/E_reference/status.json`；训练日志：`outputs/controller.stdout.log`、`outputs/controller.stderr.log`；启动记录：`outputs/LAUNCH.json`。本轮未 push。