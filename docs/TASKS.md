# SurgAgent-Bench 任务设计详解

## 五大任务家族

### Task 1: Surgical Tool-use / Measurement Task 🎯

**定位**：最核心的任务类型，最有 Agent 味道。

**任务模板**：
```
给定一段显微镜下手术视频，请判断 [测量目标] 是否 [满足/超出] [安全条件]，
并输出证据帧、关键点坐标、目标区域、测量值和风险等级。
```

**示例任务列表**：

| ID | 任务描述 | 必需工具 |
|----|---------|---------|
| T1-01 | 判断 needle tip 到角膜表面距离是否 < 安全阈值 | get_frame, localize_needle_tip, segment_tissue, estimate_depth, measure_distance, retrieve_rule |
| T1-02 | 判断 forceps tip 是否接触眼表 | get_frame, segment_instrument, segment_tissue, measure_distance |
| T1-03 | 判断 needle tip 视野内可见性 | get_frame, localize_needle_tip |
| T1-04 | 计算两个器械之间的最短距离 | get_frame, segment_instrument(x2), measure_distance |
| T1-05 | 判断 NDI 追踪与图像定位是否一致 | get_frame, localize_needle_tip, query_ndi, project_3d_to_2d |

**评估变量**：
- 正面/侧面视角
- 不同照明条件
- 有无反光/遮挡
- 不同深度（近/中/远）

---

### Task 2: Surgical Scene Understanding Task

**定位**：场景结构化理解，要求 Agent 调用感知工具后给出结构化判断。

**子任务**：

| 子任务 ID | 描述 | 输出格式 |
|-----------|------|---------|
| T2-01 | 识别当前画面中的器械类型 | {instruments: [...], confidence: ...} |
| T2-02 | 识别可见组织区域 | {tissues: [...], masks: [...]} |
| T2-03 | 判断器械-组织接触关系 | {relation: "contact"/"near"/"separated"} |
| T2-04 | 评估图像质量（反光/模糊/遮挡） | {issues: [...], severity: ...} |
| T2-05 | 描述器械与组织的空间关系 | {spatial_desc: "tool above cornea"} |

**评估指标**：
- Classification Accuracy / Weighted F1
- Segmentation IoU / Dice (if applicable)
- Contact Relation Accuracy
- Image Quality F1
- Spatial Relation Accuracy

---

### Task 3: Surgical Workflow / Phase Reasoning Task

**定位**：时序推理，理解手术流程。

**猪眼前节实验的简化阶段定义**：

```
Phase 0: preparation       # 视野建立，器械准备中
Phase 1: insertion         # 器械进入视野
Phase 2: approach          # 器械靠近眼表
Phase 3: contact           # 器械接触/定位
Phase 4: manipulation      # 操作执行
Phase 5: withdrawal        # 器械退出
```

**任务示例**：

| ID | 描述 |
|----|------|
| T3-01 | 给定当前帧，判断属于哪个阶段 |
| T3-02 | 给定阶段序列 [P1, P2, ?]，预测缺失阶段 |
| T3-03 | 预测下一帧可能的动作 |
| T3-04 | 判断是否发生了阶段转换 |
| T3-05 | 时序异常检测（跳过阶段/逆向阶段） |

---

### Task 4: Surgical Safety / Risk Detection Task 🛡️

**定位**：临床意义最强，聚焦风险识别与安全提醒。

**风险标签体系**：

| 风险类别 | 子类型 | 描述 |
|---------|--------|------|
| **spatial_risk** | distance_too_close | 器械到组织距离过小 |
| | unexpected_contact | 非预期的器械-组织接触 |
| | boundary_crossing | 器械跨越安全区域边界 |
| **perception_risk** | tip_occluded | 针尖被遮挡 |
| | tip_out_of_view | 针尖不在视野内 |
| | specular_reflection | 高光影响深度估计 |
| | low_depth_confidence | 深度置信度过低 |
| **tracking_risk** | ndi_lost | NDI 追踪丢失 |
| | calibration_mismatch | 图像-NDI 标定不一致 |
| **uncertainty_risk** | measurement_unreliable | 综合测量不可靠 |

**安全评估优先级**：

```
高风险召回率 (Critical Risk Recall) > 误安全率 (False Safe Rate) > 其他指标
```

---

### Task 5: Surgical Report / Teaching Feedback Task

**定位**：与医学教育和手术训练结合。

**任务示例**：

| ID | 描述 |
|----|------|
| T5-01 | 观察训练视频，生成器械稳定性评价 |
| T5-02 | 评价器械靠近目标区域的效率 |
| T5-03 | 识别不必要移动 |
| T5-04 | 判断关键步骤是否完成 |
| T5-05 | 生成总体技能评分 + 改进建议 |

**参考 JIGSAWS 技能维度**：

| 维度 | 含义 |
|------|------|
| Economy of Motion | 动作经济性 |
| Bimanual Dexterity | 双手协调性 |
| Tissue Handling | 组织处理 |
| Suture Quality | 缝合质量 |

---

## 任务难度分级

| 难度 | 工具数量 | 调用步数 | 视觉难度 | 示例 |
|------|---------|---------|---------|------|
| **Easy** | 1-2 | 2-3 | 清晰、正面、无遮挡 | 识别器械类型 |
| **Medium** | 3-4 | 4-6 | 轻微反光或部分遮挡 | 计算距离 + 风险判断 |
| **Hard** | 5+ | 7+ | 严重反光、遮挡、低纹理 | 综合风险评估 + 不确定性说明 |

---

## 从"看图回答"到"Agent 任务"的转换

| 传统 VQA | Agent 任务版本 |
|----------|---------------|
| "图中有什么器械？" | "调用 segment_instrument 识别器械，并用 localize_needle_tip 定位针尖，输出结构化结果。" |
| "这个阶段是什么？" | "调用 get_frame 取当前帧，结合 find_relevant_frames 分析时序上下文，输出阶段判断及证据。" |
| "器械离眼表近吗？" | "调用 get_frame → localize_needle_tip → estimate_depth → measure_distance → retrieve_safety_rule，输出距离值和风险等级。" |
