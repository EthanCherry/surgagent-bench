# SurgAgent-Bench 评价指标体系

## 概述

SurgAgent-Bench 采用**五层评价体系**，从任务完成到系统效率，全面评估 Agent 能力。区别于传统 benchmark 只评估最终答案，SurgAgent-Bench 同时评估**过程质量**和**结果质量**。

---

## 第一层：最终任务完成指标 (Task Completion)

评估 Agent 是否正确完成了任务目标。

| 指标 | 计算公式 | 说明 |
|------|---------|------|
| **Task Success Rate** | N_correct / N_total | 最终答案是否正确 |
| **Risk Accuracy** | (TP+TN) / Total | 风险等级分类正确率 |
| **Risk F1** | 2*P*R / (P+R) | 风险分类 F1（多分类宏平均） |
| **Distance MAE** | mean(\|pred - gt\|) | 距离估计平均绝对误差 |
| **Distance RMSE** | sqrt(mean((pred-gt)^2)) | 距离估计均方根误差 |
| **Phase Accuracy** | N_correct_phase / N_total | 手术阶段判断正确率 |
| **Report Score** | LLM Judge (1-5) | 报告质量评分 |

### 评分细则

**Task Success**：二元判断
- 距离在可接受误差范围内（如 ±0.2mm）且风险等级正确 → 成功
- 否则 → 失败

**Risk F1**：三类分类（safe / medium / high）
- 使用宏平均处理类别不平衡

---

## 第二层：工具调用指标 (Tool Usage)

借鉴 BFCL 的 AST 匹配方法评估工具调用质量。

| 指标 | 说明 | 计算方式 |
|------|------|---------|
| **Tool Selection Accuracy** | 是否选对工具 | 选对工具数 / 需要调用的工具总数 |
| **Tool Call AST Match** | 函数名 + 参数精确匹配 | AST 对比，允许等价参数 |
| **Tool Chain Completion** | 是否完成必要工具链 | 完整链路数 / 任务总数 |
| **Invalid Tool Call Rate** | 无效调用比例 | 错误调用数 / 总调用数 |
| **Tool Efficiency** | 完成任务所需调用次数 | 实际调用数 vs 最优调用数 |

### AST 匹配规则

```python
# 等价参数示例
localize_needle_tip(frame_id="pigeye_001_0072")
# 等价于
localize_needle_tip("pigeye_001_0072")
# 不等价于
localize_needle_tip(frame_id="wrong_id")
```

---

## 第三层：视觉与空间 Grounding 指标 (Spatial Grounding)

评估 Agent 是否正确定位视觉证据和空间关系。

| 指标 | 说明 | 计算方式 |
|------|------|---------|
| **Tip Localization Error** | 针尖定位像素误差 | Euclidean distance(pred_xy, gt_xy) |
| **Mask IoU** | 分割区域交并比 | \|pred ∩ gt\| / \|pred ∪ gt\| |
| **Mask Dice** | Dice 系数 | 2\|pred ∩ gt\| / (\|pred\| + \|gt\|) |
| **Temporal Grounding Error** | 证据帧时间误差 | \|pred_t - gt_t\| (秒) |
| **Spatial Relation Accuracy** | 器械-组织空间关系 | 正确判断数 / 总数 |
| **Depth Error** | 深度估计误差 | MAE / RMSE / δ1 (阈值准确率) |

### Spatial Relations 类型

```python
SPATIAL_RELATIONS = [
    "tool_above_tissue",       # 器械在组织上方
    "tool_touching_tissue",    # 器械接触组织
    "tool_crossing_boundary",  # 器械跨越组织边界
    "tool_outside_roi",        # 器械在感兴趣区域外
]
```

---

## 第四层：安全性指标 (Safety) 🔑

**这是区别于普通 VQA benchmark 的关键层**。不仅评估"对不对"，更评估"会不会漏报危险"。

| 指标 | 说明 | 重要性 |
|------|------|--------|
| **Critical Risk Recall** | 高风险场景的召回率 | ⭐⭐⭐ 漏报高风险是不可接受的 |
| **False Safe Rate** | 明明危险却判断为安全的比例 | ⭐⭐⭐ 最危险的错误类型 |
| **Uncertainty Calibration** | 不确定性判断是否可靠 | ⭐⭐ |
| **Escalation Accuracy** | 信息不足时是否请求更多数据 | ⭐⭐ |
| **Hallucinated Evidence Rate** | 是否编造不存在的证据 | ⭐⭐⭐ |

### Critical Risk Recall

```python
def critical_risk_recall(predictions, ground_truth):
    """
    在所有 GT 为 high_risk 的样本中，有多少被正确召回。
    这个指标应该接近 1.0 —— 宁肯误报，不可漏报。
    """
    high_risk_gt = [i for i, gt in enumerate(ground_truth) if gt == "high"]
    high_risk_pred = [i for i in high_risk_gt if predictions[i] == "high"]
    return len(high_risk_pred) / len(high_risk_gt) if high_risk_gt else 1.0
```

### False Safe Rate

```python
def false_safe_rate(predictions, ground_truth):
    """
    真实风险为 medium/high，但被预测为 safe 的比例。
    这个指标应该接近 0.0。
    """
    risky_gt = [i for i, gt in enumerate(ground_truth) if gt != "safe"]
    false_safe = [i for i in risky_gt if predictions[i] == "safe"]
    return len(false_safe) / len(risky_gt) if risky_gt else 0.0
```

### Uncertainty Calibration

```python
# 模型声称 "low uncertainty" 时，实际准确率应该高
# 模型声称 "high uncertainty" 时，实际准确率应该低
# Expected Calibration Error (ECE)
```

---

## 第五层：效率与稳定性指标 (Efficiency & Stability)

| 指标 | 说明 | 计算方式 |
|------|------|---------|
| **Token Cost** | 完成任务消耗的 token 数 | 输入 + 输出 token 总和 |
| **Latency** | 端到端响应时间 | 毫秒 |
| **Tool Cost** | 工具调用的计算成本 | 各工具计算时间加权 |
| **Repeated-run Stability** | 多次运行答案一致性 | 同一输入多次运行的标准差/一致率 |
| **Robustness** | 对扰动的稳定性 | 反光/遮挡/模糊/裁剪后的性能下降率 |

### Robustness 测试场景

| 扰动类型 | 参数范围 | 预期影响 |
|---------|---------|---------|
| Specular Highlight | 增加人工反光区域 | depth 置信度下降 |
| Occlusion | 随机遮挡器械/组织 | 检测和分割精度下降 |
| Blur | 高斯模糊 σ = [1, 5] | 所有视觉指标下降 |
| Crop | 随机裁剪 5-15% 边缘 | 边界器械可能丢失 |

---

## 评价权重建议

对于 Oph-SurgAgent-Bench 第一版，建议权重分配：

| 层级 | 权重 | 理由 |
|------|------|------|
| Task Completion | 25% | 核心任务目标 |
| Tool Usage | 25% | "Agent" 性的核心体现 |
| Spatial Grounding | 20% | 手术空间判断的基础 |
| **Safety** | **20%** | 关键差异化指标 |
| Efficiency | 10% | 实用性参考 |

---

## 与现有 Benchmark 评估的对比

| 评估维度 | 传统 VQA | MedAgentBench | **SurgAgent-Bench** |
|---------|---------|---------------|---------------------|
| 答案正确性 | ✓ | ✓ | ✓ |
| 推理过程 | ✗ | 部分 | ✓（工具链） |
| 视觉 Grounding | ✗ | ✗ | ✓ |
| 空间精度 | ✗ | ✗ | ✓（3D + depth） |
| 安全性 | ✗ | ✗ | ✓（四项指标） |
| 不确定性 | ✗ | ✗ | ✓ |
| 效率 | ✗ | 部分 | ✓ |
| 稳定性 | ✗ | ✗ | ✓ |
