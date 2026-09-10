# SynAP-Fib：SFibAI 基础上的三任务自动搜索实施指令

这是一个新的研究实施任务，不是对旧实验结论的改写。请在当前 Codex 会话中实际检查、实现、测试，并执行现有权限和资源允许执行的步骤。不要只回复方案；不要承诺一定超过基线；不要把已提交的训练作业写成已经完成。

## 1. 目标与工作范围

目标仓库： https://github.com/StatXzy7/SynAP-Fib
参考审阅版本：356576445f51c7b2b302b46f339658377682262d（2026-09-10）。先记录本地实际 HEAD、git status 和与参考版本的差异，不能回滚或覆盖用户未提交的工作。

在 SFibAI 的细粒度分级系统上，实施有限预算的自动架构、数据处理及训练配方联合搜索。最终部署模型必须仅从同一张输入图像预测：

- 36-bin 纤维化分布、0.0–3.5 连续分数和既有四级结果；
- 六种 position_norm 的预测概率和类型；
- 病灶区域的预测热图及可回映到输入 ROI 坐标的预测区域/框。

主目标是在 Data V4 原生划分及既有 canonical evaluator 下，取得优于同协议 SFibAI 的分级性能，同时保留并验证两个辅助任务。主线优先保留 ResNet-50、36-bin 输出和 SFibAI 分级语义，搜索新增结构、梯度路由和训练方法。更换大主干只能是另列的扩展实验，不能把其收益直接归因于原 SFibAI 上的新增模块。

只使用现有 Data V4 及其既有标注，不以收集新数据或新人工标注为前提。既有通用预训练可以使用，但必须记录来源并给基线同等条件。公开 SFibAI 或其他医学 checkpoint 在未证明未接触当前 holdout 患者前，不得用来初始化、蒸馏或生成伪标签。

## 2. 新旧协议隔离

先阅读根目录及相关子目录 AGENTS.md，再阅读全部相关实现、测试和配置。至少覆盖：

- code/src/sfibai_b/{model,loss,data,evaluation,prediction,runner,training,protocol,bootstrap,queue,gate,storage,snapshot,benchmark,ranking}.py
- code/tests/ 下相关测试；code/configs/；code/EVALUATION_POLICY.md；code/docs/FORMAL_PROTOCOL.md
- docs/PROVENANCE.md；paper/en/tables/ 中的既有结果；必要的既有实验说明。

建立新的研究分支 research/synap-autosearch-v1 和 research/autosearch/ 工作区；分支已存在时先检查，不覆盖。新增薄的局部 AGENTS.md 指向本协议。旧 AE_COR_v2 的固定 A–G、detach、固定优化器和旧队列规则仅用于旧实验复现，不是本轮搜索空间的上限；本用户指令明确授权在新研究范围内搜索它们。

不得修改 reproducibility/、旧 round snapshots、旧结果、旧论文数字、原始数据或原生划分。优先用新包和适配器复用纯函数，不要把旧 ARM_BRANCHES 无限制扩写成整个搜索系统。禁止为适应新研究而静默改变旧 evaluator 的数值语义。

## 3. Test 使用与公平比较

原生划分保持：train 83,722 images / 4,906 patients / 35 centers；val 20,880 / 1,227 / 33；test 4,107 / 240 / 4。以实际清单、指纹与既有锁定记录核实，不能只相信本文数字。无法核实时记录阻塞，不伪造通过。

只有 native train 可用于反向传播、特征统计拟合、自监督、蒸馏训练和伪标签学习。为架构搜索在 native train 内建立患者级内层划分/分组交叉验证；折内所有训练、教师和派生缓存也必须只使用对应 inner train。不得把同一患者的图像、裁剪或伪标签分散进不同折。

搜索进程只接收去除 test 行的开发清单及允许的 train/inner-val/native-val 结果，不接收 test 图像、标签、预测和逐病例错误。独立数据审计器可核实原生清单身份和重复/泄漏，但不得将 test 表现反馈给搜索。

旧 test 已有历史评估记录，不能声称从未被接触。写明 historical_test_exposure=true。本轮从现在开始隔离搜索，不会追溯性地恢复旧 test 的盲性。最终在该 test 上的改进属于这个既有基准上的结果，不自动等于新的外部临床验证。

彻底隔离旧训练结束后自动评估 best/last test 的行为。新 search 模式不创建 test DataLoader、不调用 test evaluator、不读取旧 test leaderboard 来挑模型。只允许独立 final-test 命令在冻结清单完整后评估预先指定的模型。最终结果不再反馈到同一研究轮继续搜索。

冻结 architecture/config、所有 seed、checkpoint SHA256、训练与推理预处理、阈值、校准、集成规则和比较清单后才能打开 test。冻结后可以做不改变预测的完整性检查；发生影响数值的修复则另建研究轮并披露，不能静默更换提交模型。

## 4. 必须先完成的代码与标签审计

输出 CURRENT_AUDIT.md，逐条给出文件、函数和证据，并把会影响搜索有效性的检查实现成测试。

A. 梯度拓扑：当前 position_head(global_features.detach()) 和 lesion_head(layer3_features.detach().float()) 使辅助损失不直接更新 backbone；辅助 posterior/attention 注入分级时又被 detach。核对当前实际版本。旧 F 虽然训练辅助头，但不注入，不能作为“辅助损失改善共享表征”的直接证明。

分别对 grading、position、lesion loss 单独 backward，生成 loss × parameter-group 梯度矩阵。比较旧 A/F 在同一 FP32 batch、相同共享权重、无全局梯度裁剪等耦合时的共享梯度。AMP 的共享 GradScaler、跳步等数值耦合另行记录，不声称整个训练必然逐位相同。检查旧 G 的 warm-up 是否只是影响辅助头训练及间接数值行为，而不是共享表征的辅助梯度。

B. 数据语义：核实六类 position_norm 的真实映射、缺失和不平衡，不能编造解剖名称。检查病灶标注是框、掩膜还是其他形式，坐标是 roi_crop 还是原始图；核实 annotations 中逐病灶 severity 与 image_label_max 的关系、标注完整性和阴性定义。

C. 区域目标：当前 _lesion_target 选择最高分病灶框并集，它不是所有病灶，也不是真实轮廓。区分 max-grade evidence map 与 all-positive-lesion region；其他低分病灶不能因不在最高分框内就被当作“所有病灶任务”的负样本。未标注不等于正常。核对 loss 中 labels>0 排除的是 score=0.0 还是临床 F0(<0.5)，为边界值写测试，不能混用两种含义。

D. 分级损失：审计局部 KL 的边界 bin 与 clamp 重复索引、连续分数/bin 单位、边界惩罚和训练/评测的一致性。旧行为保持可复现；修订损失只能成为命名清楚的新候选，不能偷偷修正基线。

E. 数据与推理泄漏：核实预处理 ROI 是否依赖人工病灶标签；新旧模型应获得同等输入。推理 forward 不能读取真实位置、框、mask、病灶等级、患者 ID 或中心标签。GT 框只可参与训练监督或独立评测，不可作为 val/test 的裁剪提示、检测提示或位置路由。

## 5. 固定评估与候选可行性

唯一主终点保持：
R_final = 0.4*R_image + 0.4*R_patient_max + 0.2*R_center_balanced_patient_max，越低越好。

连续分数保持 sum(p[k]*k/10)，四级边界 0.5/1.5/2.5 且边界进入高等级。基础 COR、true/pred 对称 patient-max 和中心内 patient-max 后按 sqrt(n_center) 加权，全部复用旧 evaluator。不要将 center-balanced 改成简单中心平均，不得通过把 patient-max 改成 median 获得主终点改进。

建立 A_legacy、E_reference，以及 A_tuned 三组控制。A_tuned 保留 SFibAI 分级架构，允许相同的训练配方优化。新方法须与 A_tuned 比较，另报告对 A_legacy 的结果；不能用更多调参对照一个刻意欠优化的基线。对共享结构使用配对初始化、数据次序和相同环境；架构机制消融固定训练配方，系统整体比较披露所有改变与预算。

搜索目标是约束优化，不是把分级、位置和病灶任意加成一个可相互抵偿的分数：先满足三项输出与辅助质量约束，再最小化开发集 R_final。

先在相同开发协议下重新测量 E_reference，冻结其 position macro-F1 与 max-grade weak-box IoU@0.5 作为开发阶段的最低参考；默认不接受辅助均值退化。最终 test 的辅助比较使用同一 test 上预指定 E_reference 的配对结果与预先冻结的容忍度，不能把开发集绝对分数机械地当成另一分布上的通过线。约束定义、聚合方式与任何容忍度必须在新候选搜索前写入 protocol，不能根据 test 或搜索结果事后放宽。每类 recall、预测频率、位置混淆矩阵用于防止类别塌缩。

病灶输出至少提供自动预测的区域/框与置信度。按既有框计算独立定位指标并报告标注完整性；保留原 max-grade weak-box Dice/IoU 以便比较。新高分辨率图映射到旧评估网格的规则必须预先固定，并另列原分辨率指标。没有真实轮廓标注时，mask 指标只能称 weak-box agreement；不可将填满矩形框的高 Dice 当作真实病灶分割成功。

## 6. 数据处理搜索

所有新样本保留 parent_image_uid、patient_uid、original_split、recipe_version 与源标注哈希。原生文件只读，派生文件单独保存。

优先比较：原 stretch；letterbox；保持纵横比并做预先定义的标签无关裁剪。图像、框、mask 几何变换同步，记录逆变换。禁止 val/test 使用 GT 框确定输入裁剪。

增强比较原配方与保守的小角度旋转、亮度/对比度/gamma、轻量噪声方案。针对六类位置检验大幅 90° 旋转的影响，不预先断言一定有害。先检测图像是否接近灰度，不能只增加几乎无效的 saturation 搜索维度。位置语义不明时，不默认左右翻转。

训练可使用患者均衡、受限的等级/位置重采样，权重只能从相应训练分区计算，不对齐已知 test 分布。不能让多图患者和重复裁剪患者获得无上限权重。

ROI crop 必须使用可证明正确的局部标签：不得裁掉最高分病灶后仍继承全图 image_label_max。优先保留目标框与上下文，或利用已核实逐框标签监督局部头。默认不使用会破坏 max-grade 语义的无约束 MixUp/CutMix。

已有逐病灶框和等级可以用于局部 severity 监督、病灶区域学习及层次 MIL；阴性、缺标与不完整标注分别处理。伪 mask 仅在训练分区内由合法教师产生，低置信区域忽略，记录 lineage；同一伪标签不能同时作为“预测”与独立真值。

## 7. 模型与优化的分阶段搜索空间

不要做巨大笛卡尔积，也不要首先搭建重量级 one-shot NAS 超网。实现类型明确、可序列化、可恢复的 ModelConfig / TrainConfig / DataConfig，以及有限候选注册表。

第一阶段固定 ResNet-50 与分级输出，至少覆盖以下命名机制：

M0：旧 E 的忠实适配作为控制。
M1：真正共享表征的三任务模型，不做预测注入；辅助损失可回传共享主干。
M2：在 M1 上增加轻量多尺度病灶 decoder，比较 C4-only 与 C2–C5 的 FPN，明确 stride 8/4 和 decoder 宽度。
M3：在 M2 上加入 predicted-position 条件化与 predicted-lesion 局部特征融合。比较 feature residual、36-logit residual，以及用六类预测 posterior 做 soft routing 的低秩专家；不能用真实位置路由，也不能默认 hard argmax。
M4：在前述有效候选上加入逐框局部 severity / MIL 与可选 patient-aware 训练目标，保持最终单图推理契约和原 patient-max 评估不变。

辅助损失到 backbone 的梯度与 grading 到辅助预测的梯度是两条独立搜索轴，不可只设置一个含糊的 detach 开关。至少支持全 detached、辅助→主干可训练而预测注入 stop-grad、以及受控的联合训练。

可用 h_eta = stopgrad(h) + eta*(h-stopgrad(h)) 缩放辅助梯度，比较 eta in {0,0.1,0.3,1.0}。为共享层范围、分支 adapters、辅助 loss weights 和 warm-up 设定小规模条件空间。可执行的初始候选范围：decoder 宽度 {64,128}、输出 stride {8,4}、position/lesion 外层权重各 {0.03,0.1,0.3}、辅助 warm-up {0,10,20} epochs；保留旧 G 的 20→40 调度作为单独的慢启动控制。这些是候选设置，不是已知最优值；按机制条件化，不枚举全组合。记录梯度范数/余弦；仅在观测到冲突且简单方案不足时加入 PCGrad 等候选，计入额外训练成本，不能当作保证不退化的魔法。

优先让新增分级路径以零/小残差起步，保留 baseline 初始化行为；不要同时把 gate 和 residual 置成导致整条路径无法学习的零状态。可在早期冻结 backbone 训练新头，再逐步解冻；可从仅在对应训练分区训练的 SFibAI teacher 蒸馏。蒸馏权重包含零作为消融，避免强制继承教师偏差。

训练目标优先比较旧 hybrid、合法的全分布/ordinal-CDF 补充损失，以及病灶局部等级监督；不要直接把非可微 canonical COR 当作正常反向传播损失。所有平滑 surrogate 必须明确与真正 R_final 的差异。

patient-aware 训练若只采样患者部分图像，监督目标必须对应所采样集合，不能拿完整患者最大等级监督一个未包含最大病灶的随机子集。不得把每位患者的最大等级复制为该患者所有图像的真值。

第二阶段仅对开发验证有效的结构调学习率、weight decay、loss weights、warm-up、scheduler、EMA 与输入处理。初始范围可用 backbone lr 对数区间 [3e-5,3e-4]、head/backbone lr 倍率 {1,3,10}、weight decay 对数区间 [1e-6,1e-3]、旧 StepLR 与固定完整训练 horizon 的 warm-up cosine、EMA {off,0.999}；每个 trial 的设置都需序列化。更强 backbone、大型预训练或 ensemble 另设扩展轨道；默认主结果是一份单模型架构，在各个固定 seed 独立训练，而非挑 seed 或隐含集成。

## 8. 自动搜索、晋级与训练预算

默认上限：8 个 A_tuned 配方 trial + 32 个多任务 trial（建议 24 个机制/结构探索 + 8 个入选结构配方调优）；最终候选 2 个；最终配对 seed 固定为 [34001,34002,34003]；单次完整训练 120 epochs。初始开发 seed 固定为 31001。所有默认值在运行前写入协议；不得为追求赢 test 无限追加搜索。配方调优给 A_tuned 与入选新结构各 8 次同等级资源机会；架构探索的额外 24 次计算单独披露，不能把整项研究写成双方总搜索成本完全相等。若要声称总搜索预算匹配，必须另设相同 GPU-time 上限的基线搜索对照。

使用 Optuna 的 TPE 与 successive-halving/ASHA 思路实现有限预算搜索。以安装环境的官方 API 为准并锁定版本，不能依赖不兼容的旧 constraints API。约束由控制器显式检查；不要假设被 prune 的 trial 已经过了最终辅助质量约束。

先用一批机制明确的候选校准学习曲线，再由搜索器提议后续组合。默认晋级资源 30→60→120 epochs；正式 best 只在 epoch>20 中依既有顺序选择。剪枝前必须让该候选的辅助 warm-up 完成并有足够有效训练；对旧 G 等 epoch40才满权重的慢启动控制，不得在30epoch简单淘汰，使用单独的保护/全程评估。

小分辨率、训练子集和短程训练只能筛选，先检验这些代理对候选排序的可靠性。晋级比较必须在同资源、同开发样本下进行。不要把不同资源层级的最优分数混成一张正式榜。120epoch 的 scheduler 不得在30epoch trial中按总长擅自重缩放。

内层搜索只用 native train 内的分组划分。短名单再在完整 native train 上训练，用完整 native val 选择 best。最终两个候选与所有关键基线采用同一组三个 seed 和同一种硬件/软件栈；所有 seed 都保留，不选“幸运 seed”。在 native val 上按冻结的约束和平均 R_final 选一个最终候选，再生成 final manifest。不得对两个候选分别看 test 后挑较好者。

故障区分基础设施中断、OOM、数值失败与不合法候选。只有配置、数据和代码完全一致时才 strict resume。会改变科学数值的修补必须新 trial；记录失败和已消耗预算，不能隐藏失败 trial。持久化 study、配置与 scheduler 状态，以实际可恢复任务为准，不依赖聊天记忆。

## 9. 计算效率与部署契约

实测当前 GPU、显存、可用调度器和数据位置；文档里的 RTX 5090D 或 HPC 8×4090 不是当前资源可用的证明。不抢占无关作业，不擅自开付费实例。

多 GPU 优先一 GPU 一个独立 trial；需要 DDP 时另测。基于实测选择 workers/prefetch/persistent workers/pinned memory、AMP、channels_last 与 compile。不同 GPU 的速度不影响科学入选标准。零 worker 的 CPU smoke 配置必须合法。

支持 BF16 时先验证其数值稳定性；敏感的 KL/logsumexp/弱监督 reduction 可保持 FP32。保留 loss finite 与 AMP overflow/skip 记录。缓存确定性解码或预处理，不冻结随机增强；缓存 key 包含数据与处理版本。昂贵的数据全量哈希、几何核验、环境审计放在 preflight，不在每 step 重复执行。

搜索阶段只保存恢复所需 checkpoint、开发指标与必要预测；不每轮保存全量高分辨率 heatmap。最终冻结模型导出完整评测产物。记录训练 GPU-time、吞吐、参数量、峰值显存，以及三项输出全部打开时的 batch1 端到端 latency；基线使用相同口径。不能关闭辅助头后报告三任务推理速度。

## 10. 文件级交付和命令接口

优先新增 research/autosearch/，内含 pyproject.toml、configs/default.yaml、src/synap_search/、tests/、README.md；复用 code/ 中可复用的纯函数，原实验保持可运行。

必须交付：CURRENT_AUDIT.md、DATA_AUDIT.json、PROTOCOL.md、SEARCH_SPACE.yaml、环境锁定、所有 trial registry、开发 leaderboard、梯度拓扑测试结果、FINAL_MANIFEST.json，以及 FINAL_REPORT.md。小型协议、测试、脱敏配置可提交；患者清单、图像、逐图预测、权重和日志必须留在被忽略的私有输出目录，不推送到公开 GitHub。

请实现并测试下列新接口（它们是本次要求新增的接口，不是声称仓库已经存在）：

python -m pip install -e code
python -m pip install -e research/autosearch
python -m synap_search audit --config research/autosearch/configs/default.yaml
python -m synap_search smoke --config research/autosearch/configs/default.yaml
python -m synap_search search --config research/autosearch/configs/default.yaml --resume
python -m synap_search confirm --config research/autosearch/configs/default.yaml
python -m synap_search freeze --config research/autosearch/configs/default.yaml
python -m synap_search final-test --manifest PATH_TO_FINAL_MANIFEST
python -m synap_search report --manifest PATH_TO_FINAL_MANIFEST

配置从已有本地配置或环境变量发现 Data V4 和私有输出位置；PATH_TO_FINAL_MANIFEST 由 freeze 实际输出。不得填入猜测路径并宣称运行成功。提供一个只在上一阶段 gate 通过后进入下一阶段的 run-all 控制入口；没有可行候选时不得自动运行 test。

至少测试：三输出形状与范围、label/bin边界、各梯度模式、辅助 branch 的真更新、原 A/E 行为不变、paired initialization、患者派生样本无跨折、box/图像逆变换、禁止 test 访问、非法 GT 输入、原 evaluator 数值回归、canonical patient 聚合、prune/恢复一致性、cache invalidation、manifest hash和三头推理导出。

不在本任务自动 push、发布论文结论或覆盖旧表格。先给出实际变更和测试结果，必要时创建可复核的本地提交。

## 11. 最终验收与如实报告

开 test 前就冻结：唯一主要 comparison 为新候选对 A_tuned 的 R_final；其他 A_legacy、E_reference 和辅助比较为预先列明的次要比较，不能事后挑显著 contrast。

报告所有三个 seed 的配对差 Δ_s = R_new,s - R_baseline,s、均值、标准差、每个 seed 的方向，并对固定 seed 集合的平均差进行按中心分层、患者簇配对 bootstrap（10,000 次）。各模型和各 seed 使用相同患者重采样；重算实际 canonical R_final。明确该 CI 条件于这组 seed，不能把 seed×patient 当作独立扩大样本量，也不能把“bootstrap更优比例”当成 p 值或消除历史 test 自适应偏差。

主验收要求：分级平均 Δ<0；辅助任务达到冻结的质量约束；所有输出可独立从图像产生；无协议/数据泄漏；成本如实报告。将“点估计领先”与“95% CI上界<0且各seed方向一致的更强证据”分开命名。即使满足后者也不能声称外部中心/临床效用已验证。

没有真实病灶轮廓时，精确分割能力始终标为未被独立验证；定位目标可用既有框支持。没有可行候选、分级未改善、辅助任务退化或证据不足都要如实给出，不修改指标和任务定义制造成功。

FINAL_REPORT.md 首节为“Test set 主结果”；尚未执行 test 时明确写“未执行”，接着列出开发集结果。报告必须含三任务指标、全部预指定seed、成本、划分/模型/配置指纹、实际完成的命令和日志位置、限制，以及可由现有 train/val 证据支持的下一轮方向。

现在开始执行：先检查工作区和指令，再完成标签/梯度审计与搜索/测试隔离，随后实现最小可运行搜索闭环。数据或 GPU 不在当前环境时，继续完成不依赖它们的代码、单元测试和 CPU smoke，准确指出哪些步骤未运行；不得用随机数据成绩或旧论文数字代替真实训练结果。真正提交了长期作业时只报告实际 job id 和当前状态，不冒充完成或承诺稍后通知。