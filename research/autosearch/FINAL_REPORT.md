# Test set 主结果

TEST PENDING / 结果未完成。Test 未执行或产物尚不完整。

预锁定主终点：R_final = 0.4 image COR + 0.4 patient-max COR + 0.2 sqrt(center n) 加权 patient-max COR；越低越好。
本轮固定 seeds: 34001, 34002, 34003。历史 test 已有暴露；本轮搜索阶段隔离 test。


## 开发集结果与 checkpoint 选择

SEARCH_COMPLETE.json: 未完成；无可报告的正式开发排名。
CONFIRM_COMPLETE.json: 未完成；无可报告的正式开发排名。

## 指纹与完成状态

Data audit: PASS; image hashes verified: 108709.
Manifest SHA256: 73a14221ea1a67f3248351a4ed5d08574f904175e69d9129ab2e705a0bb86a40
Annotations SHA256: 6684cb633ad055eb55f399a6383f531b5e8cf4db0a3ef828fb6967c16150d167

## 限制

弱框指标是 weak-box agreement；真实轮廓分割与外部临床效用未独立验证。
未完成的训练、确认或 test 均不构成性能提升证据。成本、环境、源代码和数据指纹保存在各 trial identity/result、ENVIRONMENT、DATA_AUDIT 与 ROUND_LOCK 文件。
