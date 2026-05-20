# SurgAgent-Bench

> **面向手术场景的多模态工具调用与任务决策 Agent Benchmark**
>
> 不只问模型"这张图里有什么"，而是让 Agent 像一个手术辅助系统一样，观察视频/图像，调用工具，读取测量结果，结合手术知识，最后完成一个可验证的手术任务。

🔗 **Live Demo**: [ethancherry.github.io/surgagent-bench](https://ethancherry.github.io/surgagent-bench/)

---

## 目录

- [1. 为什么需要 SurgAgent-Bench？](#1-为什么需要-surgagent-bench)
- [2. 现有 Benchmark 全景分析](#2-现有-benchmark-全景分析)
- [3. 市场空白与创新机会](#3-市场空白与创新机会)
- [4. SurgAgent-Bench 总体设计](#4-surgagent-bench-总体设计)
- [5. 五大任务家族](#5-五大任务家族)
- [6. 工具环境设计](#6-工具环境设计)
- [7. 五层评价指标体系](#7-五层评价指标体系)
- [8. Oph-SurgAgent-Bench：眼科显微手术子集](#8-oph-surgagent-bench眼科显微手术子集)
- [9. 完整 Agent 调用流程](#9-完整-agent-调用流程)
- [10. 数据质量评估方法](#10-数据质量评估方法)
- [11. 论文结构建议](#11-论文结构建议)
- [12. 实现路线图](#12-实现路线图)
- [13. 与现有工作的差异化](#13-与现有工作的差异化)
- [14. 项目结构](#14-项目结构)
- [15. 引用](#15-引用)

---

## 1. 为什么需要 SurgAgent-Bench？

### 核心洞察

现有医学 AI benchmark 存在明显的断层：

| 层面 | 已有工作 | 缺少什么 |
|------|---------|---------|
| **通用 Agent** | GAIA, AgentBench, ToolBench, WebArena, SWE-bench | 手术场景适配 |
| **医学 Agent** | MedHELM, MedAgentBench, AgentClinic | 手术视觉 + 空间感知 |
| **手术视觉** | Cholec80, EndoVis, JIGSAWS, SurgBench, SAP-Bench | Agent 范式（工具调用 + 多步推理） |

**SurgAgent-Bench 的定位**：填补"手术场景 Agent"这一空白——评估的不是单模型能力，而是 **Agent 在手术环境中感知→调用工具→推理→决策的完整链路**。

### 设计哲学

> 不与已有手术 VQA benchmark 竞争，而是提升一个维度：从"看图回答"升级为"调用工具完成任务"。

---

## 2. 现有 Benchmark 全景分析

### 第一类：通用 LLM Agent Benchmark

评估 Agent 的通用能力：工具调用、网页操作、多步推理、任务完成率。

| Benchmark | 核心评估内容 | 对 SurgAgent-Bench 的启发 |
|-----------|-------------|--------------------------|
| **BFCL** | 函数调用 AST 匹配正确性 | 评估"是否正确调用 depth/seg/tool-detection 工具" |
| **ToolBench / ToolLLM** | 16,464 个真实 REST API，单工具/多工具链路 | 手术 Agent 可设计"工具链调用"任务 |
| **GAIA** | 466 个真实世界问题，多步推理 + 多模态 + 工具使用 | "最终答案简单，但过程复杂"的设计模式 |
| **AgentBench** | 8 类交互环境下 LLM Agent 推理和决策 | Benchmark 应评估交互过程，不只是最终答案 |
| **WebArena / OSWorld** | 812/369 个网页/真实电脑任务 | 手术 benchmark 也可做"模拟环境 + 工具接口" |
| **SWE-bench** | 解决真实 GitHub issue，用测试用例自动验证 | **最终结果必须可自动验证**——这是核心设计约束 |

### 第二类：医学 LLM / 医学 Agent Benchmark

医学领域已从"考试题 QA"转向"真实临床任务 Agent"。

| Benchmark | 核心内容 | 局限 |
|-----------|---------|------|
| **MedHELM** | 临床决策、病历生成、患者沟通、医学研究、行政流程 | 偏通用医疗文本，非手术现场 |
| **MedS-Bench** | 11 类临床任务（诊断、治疗建议、报告总结等） | 主要是语言/临床文本任务 |
| **MedAgentBench** | Agent 在 FHIR 电子病历环境中完成 300 个临床任务 | 重点在 EHR，不是手术视频 |
| **AgentClinic** | 模拟临床环境，患者交互 + 多模态数据采集 + 工具使用 | 主要是问诊/诊断，非手术操作 |
| **MedAgentsBench** | 复杂医学推理、诊断和治疗规划 | 偏 reasoning，非视觉-动作闭环 |

**关键发现**：MedAgentBench 证明"不是让模型直接答题，而是让 Agent 在虚拟环境中完成任务"是可行的评估范式——这对 SurgAgent-Bench 是最直接的参考。

### 第三类：手术 AI / 手术多模态 Benchmark

手术领域视觉 benchmark 丰富，但尚未 Agent 化。

| Benchmark / 数据集 | 主要任务 | 启发 |
|-------------------|---------|------|
| **Cholec80** | 胆囊切除术 phase recognition + tool presence | 手术流程理解任务 |
| **EndoVis Challenge** | 机器人手术器械分割、场景分割 | 工具分割/器械识别 ground truth |
| **JIGSAWS** | 缝合、打结、穿针等机器人手术技能评估 | 技能评价 + 动作序列分析 |
| **SurgBench** | 72 个任务：phase, tool, action, organ 等 | 手术视频任务可系统化组织 |
| **SurgVLM-Bench / SurgMLLMBench** | 手术多模态理解、VQA、分割 | 接近 MLLM benchmark，但 Agent 性不够 |
| **SAP-Bench** | 根据当前画面预测下一步动作 | 与"手术 Agent 决策"最接近 |
| **SurgViVQA / SurgTEMP** | 手术视频问答，强调时序和视频上下文 | 手术任务必须考虑 temporal reasoning |

---

## 3. 市场空白与创新机会

### 一句话总结

> **现有医学 Agent benchmark 关注 EHR、问诊、诊断推理；现有手术 benchmark 关注图像/视频理解、器械分割、阶段识别、动作预测。但缺少一个专门评估"手术场景下 Agent 如何感知、调用工具、推理、做风险判断和生成可验证行动建议"的 benchmark。**

### 三个维度的创新

| 维度 | 传统手术 Benchmark | SurgAgent-Bench |
|------|-------------------|-----------------|
| **交互范式** | 输入图像/视频，输出类别或文本 | 输入任务目标，Agent 可多轮调用工具 |
| **评估方式** | 只评估最终答案 | 同时评估工具调用路径、测量过程、最终判断 |
| **空间维度** | 多数是 2D 视觉理解 | 可加入真实尺度 depth / NDI / 3D 信息 |
| **系统定位** | 偏模型能力 | 偏手术辅助系统能力 |

---

## 4. SurgAgent-Bench 总体设计

### 定义

> **SurgAgent-Bench** 是一个面向手术场景的多模态 Agent 评估基准，评估大模型 Agent 在手术图像/视频环境中进行**视觉感知、工具调用、空间测量、流程理解、风险识别与下一步任务规划**的能力。

### 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    SurgAgent-Bench                       │
├─────────────────────────────────────────────────────────┤
│  Task Families                                           │
│  ├── Task 1: Surgical Tool-use / Measurement            │
│  ├── Task 2: Surgical Scene Understanding               │
│  ├── Task 3: Surgical Workflow / Phase Reasoning        │
│  ├── Task 4: Surgical Safety / Risk Detection           │
│  └── Task 5: Surgical Report / Teaching Feedback        │
├─────────────────────────────────────────────────────────┤
│  Tool Environment                                        │
│  ├── Visual Perception Tools (get_frame, segment, ...)  │
│  ├── Depth & Spatial Tools (estimate_depth, NDI, ...)  │
│  ├── Temporal Tools (find_frames, action_recognition)   │
│  ├── Knowledge Tools (retrieve_safety_rule, ...)        │
│  └── Verification Tools (report, uncertainty_check)     │
├─────────────────────────────────────────────────────────┤
│  Evaluation (5 Layers)                                   │
│  ├── L1: Task Completion                                │
│  ├── L2: Tool Usage                                     │
│  ├── L3: Visual & Spatial Grounding                     │
│  ├── L4: Safety                                         │
│  └── L5: Efficiency & Stability                         │
└─────────────────────────────────────────────────────────┘
```

### 输入/输出格式

**输入**（每个样本）：
```json
{
  "case_id": "pigeye_001",
  "input_type": "video_clip",
  "video_clip": "xxx.mp4",
  "task_instruction": "判断当前针尖到眼表的距离是否处于风险范围，并给出证据。",
  "available_tools": [
    "frame_reader",
    "needle_tip_detector",
    "tissue_segmenter",
    "depth_estimator",
    "ndi_query",
    "distance_calculator",
    "surgical_knowledge_retriever"
  ]
}
```

**Agent 预期输出**：
```json
{
  "answer": "当前针尖距离眼表较近，属于中风险。",
  "risk_level": "medium",
  "evidence_timestamp": "00:07.2",
  "needle_tip_xy": [612, 384],
  "target_region": "corneal_surface",
  "distance_mm": 0.83,
  "tool_calls": [
    "frame_reader",
    "needle_tip_detector",
    "depth_estimator",
    "distance_calculator"
  ],
  "uncertainty": "moderate",
  "reason": "针尖位于眼表上方，深度差较小，但局部存在反光，测量置信度中等。"
}
```

**Ground Truth**：
```json
{
  "risk_level": "medium",
  "evidence_timestamp_range": ["00:07.0", "00:07.5"],
  "needle_tip_xy": [608, 386],
  "target_region_mask": "mask_001.png",
  "distance_mm": 0.79,
  "acceptable_error_mm": 0.2
}
```

---

## 5. 五大任务家族

### Task 1：Surgical Tool-use / Measurement Task 🎯 核心

**任务描述**：Agent 需要调用多个感知/测量工具，完成手术场景中的空间测量和判断。

**示例任务**：
> 给定一段显微镜下猪眼手术视频，请判断当前 needle tip 到角膜/眼表最近距离是否小于安全阈值，并输出证据帧、针尖坐标、组织区域、距离值和风险等级。

**可调用工具**：
```
get_frame()           → 读取视频帧
segment_instrument()   → 分割器械
localize_needle_tip()  → 定位针尖
estimate_depth()       → 双目深度估计
query_ndi_tip_position() → NDI 3D坐标
measure_tip_to_surface_distance() → 距离计算
retrieve_surgical_rule() → 安全规则
```

**评估指标**：

| 指标 | 含义 |
|------|------|
| Tool Call Accuracy | 是否调用了正确工具 |
| Parameter Accuracy | 工具参数是否正确（timestamp, ROI, target tissue） |
| Distance Error | 预测距离与 GT 的 MAE / RMSE |
| Risk Accuracy | 风险等级分类是否正确 |
| Evidence Grounding | 是否给出正确证据帧/区域 |
| Efficiency | 工具调用次数、token 成本、耗时 |

### Task 2：Surgical Scene Understanding Task

**任务描述**：Agent 调用感知工具后，对手术场景进行结构化理解。

**子任务**：

| 子任务 | 输出 |
|--------|------|
| 器械识别 | needle / forceps / cystotome / hook |
| 组织识别 | cornea / lens / iris / sclera / tissue surface |
| 接触关系 | contact / near-contact / separated |
| 图像质量 | specular highlight / blur / occlusion |
| 空间关系 | tool above tissue / tool crossing boundary |

**评估指标**：Classification Accuracy / F1, Segmentation IoU / Dice, Contact Relation Accuracy, Image Quality F1, Grounding IoU

### Task 3：Surgical Workflow / Phase Reasoning Task

**任务描述**：Agent 理解手术流程，判断当前阶段并预测下一步。

**猪眼前节实验流程**（示例）：
```
1. 视野建立 → 2. 器械进入 → 3. 靠近眼表 → 4. 接触/定位 → 5. 操作执行 → 6. 器械退出
```

**评估指标**：

| 指标 | 含义 |
|------|------|
| Phase Accuracy | 当前阶段识别准确率 |
| Step Transition Accuracy | 上一步/下一步预测准确率 |
| Temporal Localization Error | 预测时间点与真实时间点误差 |
| Action Sequence Edit Distance | 预测动作序列与真实序列的编辑距离 |
| Evidence Consistency | 解释是否与视频证据一致 |

### Task 4：Surgical Safety / Risk Detection Task 🛡️

**任务描述**：识别手术场景中的安全风险，给出风险判断和不确定性说明。

**风险标签体系**：

| 风险类型 | 示例 |
|---------|------|
| distance risk | needle-to-surface distance 过小 |
| occlusion risk | 器械尖端被遮挡，定位不可靠 |
| reflection risk | 高光区域影响 depth |
| out-of-view risk | needle tip 不在视野内 |
| unstable estimation | depth uncertainty 高 |

**评估指标**：
- Risk Classification F1
- **False Negative Rate**（尤其重要——漏报风险要严惩）
- **Uncertainty Calibration**（模型说"不确定"时是否真的不可靠）
- **Safe Escalation Rate**（信息不足时是否请求更多数据）

### Task 5：Surgical Report / Teaching Feedback Task

**任务描述**：观察训练视频，生成结构化教学反馈。

**评估指标**：

| 指标 | 含义 |
|------|------|
| Skill Score Correlation | 与专家评分的 Spearman / Pearson 相关 |
| Event Detection F1 | 是否识别到关键错误或关键动作 |
| Feedback Quality | 专家评分或 LLM Judge |
| Evidence Coverage | 是否引用了正确时间片段 |

---

## 6. 工具环境设计

Agent 不直接操作手术机器人，而是通过一组 **可调用的函数/API** 获取证据并做出判断。

> **Agent = 大模型大脑**
> **工具 = 外部感知/测量/检索/计算模块**
> **Benchmark = 看它会不会正确选择工具、传入参数、读取结果，并做出最终判断**

### 6.1 视觉感知工具

```python
# 1. 读取视频帧
def get_frame(video_id: str, timestamp: str) -> dict:
    """从手术视频取某一时刻的图像"""
    return {
        "frame_id": "pigeye_001_0072",
        "image": "frame_0072.png"
    }

# 2. 器械分割
def segment_instrument(frame_id: str) -> dict:
    """分割图像中的针、镊子、器械区域"""
    return {
        "instrument_mask": "mask_instrument.png",
        "instrument_type": "needle",
        "confidence": 0.91
    }

# 3. 针尖定位
def localize_needle_tip(frame_id: str) -> dict:
    """输出 needle tip 的 2D 坐标"""
    return {
        "tip_xy": [612, 384],
        "confidence": 0.87
    }

# 4. 组织区域分割
def segment_tissue(frame_id: str, target: str = "cornea") -> dict:
    """分割角膜、巩膜、晶状体表面、眼表区域"""
    return {
        "target": "corneal_surface",
        "mask": "mask_cornea.png",
        "confidence": 0.89
    }
```

### 6.2 深度与空间测量工具

```python
# 5. 深度估计
def estimate_depth(
    left_frame_id: str,
    right_frame_id: str,
    camera_params: dict
) -> dict:
    """输入双目图像和相机参数，输出 dense depth"""
    return {
        "depth_map": "depth_0072.npy",
        "unit": "mm",
        "valid_region": "valid_mask.png",
        "confidence_map": "conf_0072.npy"
    }

# 6. NDI 查询
def query_ndi_tip_position(
    timestamp: str,
    coordinate: str = "camera"
) -> dict:
    """查询 NDI 记录的针尖 3D 坐标"""
    return {
        "tip_xyz_camera": [3.2, 1.5, 42.8],
        "unit": "mm",
        "tracking_status": "valid"
    }

# 7. 坐标投影
def project_3d_to_2d(
    point_xyz_camera: list,
    camera_intrinsics: dict
) -> dict:
    """把 NDI 3D 点投影回显微镜图像"""
    return {
        "uv": [610, 386],
        "reprojection_error": 1.8
    }

# 8. 针尖到组织表面距离计算 ← 核心工具
def measure_tip_to_surface_distance(
    tip_xyz: list,
    surface_depth_map: str,
    tissue_mask: str
) -> dict:
    """计算 needle tip 到眼表/角膜表面的最近距离"""
    return {
        "distance_mm": 0.83,
        "nearest_surface_point": [604, 390],
        "risk_level_by_threshold": "medium"
    }
```

### 6.3 视频时序工具

```python
# 9. 关键帧检索
def find_relevant_frames(
    video_id: str,
    query: str = "needle approaching eye surface"
) -> dict:
    """从视频中找出关键事件时刻"""
    return {
        "timestamps": ["00:05.8", "00:07.2", "00:08.1"],
        "event": "needle_approaching_surface"
    }

# 10. 动作识别
def recognize_surgical_action(video_clip: str) -> dict:
    """识别当前动作类型"""
    return {
        "action": "approach",  # approach/contact/puncture-like/withdraw/idle
        "confidence": 0.84
    }
```

### 6.4 规则与知识检索工具

```python
# 11. 安全阈值检索
def retrieve_safety_rule(task: str = "needle_to_eye_distance") -> dict:
    """读取 benchmark 设定的风险判断规则"""
    return {
        "safe_distance_mm": 1.0,
        "medium_risk_range": [0.5, 1.0],
        "high_risk_range": [0.0, 0.5],
        "note": "This threshold is defined for benchmark evaluation, not clinical use."
    }

# 12. 病例信息检索
def retrieve_case_info(case_id: str) -> dict:
    """读取当前样本的 metadata"""
    return {
        "case_id": "pigeye_001",
        "task": "needle-to-eye distance assessment",
        "camera": "stereo microscope",
        "calibration_available": True,
        "ndi_available": True
    }
```

### 6.5 结果验证与报告工具

```python
# 13. 结构化报告生成
def generate_structured_report(
    measurements: dict,
    observations: dict
) -> dict:
    """输出结构化结果"""
    return {
        "risk_level": "medium",
        "distance_mm": 0.83,
        "evidence_frame": "00:07.2",
        "reason": "Needle tip is close to the eye surface but not in contact."
    }

# 14. 不确定性检查
def check_measurement_reliability(
    depth_confidence: float,
    tip_confidence: float,
    ndi_status: str
) -> dict:
    """评估测量可靠性"""
    return {
        "reliability": "moderate",
        "main_issue": "local specular reflection affects depth confidence"
    }
```

### 核心 8 工具（推荐起点）

如果从可行性出发，建议先聚焦 8 个核心工具：

| # | 工具 | 作用 |
|---|------|------|
| 1 | `get_frame` | 读取视频帧 |
| 2 | `localize_needle_tip` | 定位针尖 |
| 3 | `segment_instrument` | 分割器械 |
| 4 | `segment_eye_surface` | 分割眼表区域 |
| 5 | `estimate_depth` | 双目深度估计 |
| 6 | `query_ndi_tip_position` | 查询 NDI 针尖 3D 坐标 |
| 7 | `measure_tip_to_surface_distance` | 计算针尖到眼表距离 |
| 8 | `retrieve_safety_rule` | 读取风险判断规则 |

---

## 7. 五层评价指标体系

### 第一层：最终任务完成指标

| 指标 | 说明 |
|------|------|
| Task Success Rate | 最终答案是否正确 |
| Risk Accuracy / F1 | 风险等级是否正确 |
| Distance MAE / RMSE | 距离估计误差 |
| Phase / Action Accuracy | 阶段或动作判断是否正确 |
| Report Score | 报告质量评分 |

### 第二层：工具调用指标

借鉴 BFCL 的 AST 匹配方法：

| 指标 | 说明 |
|------|------|
| Tool Selection Accuracy | 是否选对工具 |
| Tool Call AST Match | 函数名、参数是否匹配 |
| Tool Chain Completion | 是否完成必要工具链 |
| Invalid Tool Call Rate | 无效调用比例 |
| Tool Efficiency | 完成任务所需调用次数 |

### 第三层：视觉与空间 Grounding 指标

| 指标 | 说明 |
|------|------|
| Tip Localization Error | 针尖定位像素误差 |
| Mask IoU / Dice | 组织/器械分割准确度 |
| Temporal Grounding Error | 证据帧时间误差 |
| Spatial Relation Accuracy | 器械-组织空间关系是否正确 |
| Depth Error | depth 与 GT 的误差 |

### 第四层：安全性指标 🔑

区别于普通 VQA benchmark 的关键层：

| 指标 | 说明 |
|------|------|
| **Critical Risk Recall** | 高风险场景召回率 |
| **False Safe Rate** | 明明危险却判断安全的比例 |
| Uncertainty Calibration | 不确定性是否可靠 |
| Escalation Accuracy | 信息不足时是否请求更多证据 |
| **Hallucinated Evidence Rate** | 是否编造不存在的证据 |

### 第五层：效率与稳定性指标

| 指标 | 说明 |
|------|------|
| Token Cost | token 消耗 |
| Latency | 响应时间 |
| Tool Cost | 工具调用成本 |
| Repeated-run Stability | 多次运行答案是否稳定 |
| Robustness | 对反光、遮挡、模糊、裁剪扰动的稳定性 |

---

## 8. Oph-SurgAgent-Bench：眼科显微手术子集

### 定位

> **Oph-SurgAgent-Bench** 是 SurgAgent-Bench 的眼科显微手术子集，聚焦 needle tip 空间感知和风险评估。

### 与现有猪眼数据集的结合

用户拥有的数据优势：
- 显微镜 + NDI + 猪眼前节 depth/needle distance 基准
- 真实尺度信息（大部分手术 MLLM benchmark 没有的）

**升级思路**：
> 不只是评估一个 depth model，而是评估一个 Agent 是否能正确调用 depth、segmentation、needle localization、NDI query 等工具，完成手术空间关系判断。

### 两个版本

| 版本 | 数据来源 | 难度 | 适用阶段 |
|------|---------|------|---------|
| **Oph-SurgAgent-Bench-Lite** | 公开手术图像/视频 + 人工标注 QA | 低 | 先做论文 prototype |
| **Oph-SurgAgent-Bench-3D** | 显微镜 + NDI 猪眼数据 | 高 | 作为核心创新 |

### 安全阈值设计（Benchmark 内自定义）

| 距离 | 风险 |
|------|------|
| > 1.0 mm | safe |
| 0.5–1.0 mm | medium risk |
| < 0.5 mm | high risk |

> ⚠️ 阈值仅为 benchmark 评估定义，不代表临床使用标准。

---

## 9. 完整 Agent 调用流程

以"判断 00:07.2 时刻 needle tip 到眼表距离是否危险"为例：

```
Step 1: get_frame(video_id, "00:07.2")
        → 取出左右目图像

Step 2: localize_needle_tip(frame_id)
        → 找到针尖 2D 坐标 [612, 384]

Step 3: segment_tissue(frame_id, target="eye_surface")
        → 找到眼表区域 mask

Step 4: estimate_depth(left_frame, right_frame, camera_params)
        → 得到 dense depth map

Step 5: query_ndi_tip_position("00:07.2", coordinate="camera")
        → 得到 NDI 针尖 3D 坐标 [3.2, 1.5, 42.8]

Step 6: measure_tip_to_surface_distance(tip, depth, mask)
        → 计算距离 0.83mm

Step 7: retrieve_safety_rule("needle_to_eye_distance")
        → 读取阈值规则

Step 8: 输出判断
        → risk_level: "medium", distance: 0.83mm, evidence: "00:07.2"
```

### 对比：好 Agent vs 差 Agent

| | 差 Agent | 好 Agent |
|---|---------|---------|
| 方式 | 直接看图回答"针尖好像比较近" | 取关键帧→定位→分割→深度→NDI→计算→阈值判断 |
| 可验证性 | 不可验证 | 每步都可验证 |
| 不确定性 | 不说明 | 高光/遮挡时明确标注不确定性 |
| 工具证据 | 无 | 完整工具调用链 |

---

## 10. 数据质量评估方法

借鉴 HelloAgents 12.4 的数据质量框架：

### LLM Judge 维度

| 维度 | 含义 |
|------|------|
| Clinical/Surgical Plausibility | 任务是否符合真实手术场景 |
| Visual Groundability | 问题是否能从图像/视频中找到证据 |
| Tool Necessity | 是否真的需要工具调用（而非肉眼猜答案） |
| Answer Verifiability | 是否有明确 GT 可验证 |
| Safety Relevance | 是否涉及有意义的风险判断 |
| Difficulty Match | 难度是否符合目标等级 |

### Win Rate 比较

评审模型或专家比较：
- A：自动生成的手术 Agent 任务
- B：专家人工设计的手术 Agent 任务

输出 `winner: A/B/Tie` + reason。

### 人工验证

状态标记：`approved / needs_revision / rejected`

验证重点：
- 任务是否有医学/手术意义
- 标准答案是否唯一或可判定
- 图像证据是否充分
- 是否存在幻觉式问题
- 是否会诱导模型给出不可靠建议

---

## 11. 论文结构建议

### 标题备选

1. **SurgAgent-Bench: Benchmarking Multimodal LLM Agents for Tool-Augmented Surgical Scene Understanding and Risk Assessment**

2. **Oph-SurgAgent-Bench: A Tool-Augmented Multimodal Agent Benchmark for Spatial Perception and Risk Assessment in Ophthalmic Microsurgery**

### 论文大纲

```
1. Introduction
   - 医学 LLM benchmark 已从 QA 发展到临床 Agent
   - 手术 AI benchmark 已覆盖 phase、tool、VQA、action planning
   - 但缺少针对手术场景的 Agent benchmark
   - 手术 Agent 需要多模态感知 + 工具调用 + 空间测量 + 风险判断
   - 因此提出 SurgAgent-Bench

2. Related Work
   2.1 General LLM Agent Benchmarks
       GAIA, AgentBench, ToolBench, WebArena, OSWorld
   2.2 Medical LLM / Agent Benchmarks
       MedHELM, MedS-Bench, MedAgentBench, AgentClinic
   2.3 Surgical AI Benchmarks
       Cholec80, EndoVis, JIGSAWS, SurgBench, SurgMLLMBench, SAP-Bench

3. Benchmark Construction
   3.1 数据来源与手术场景划分
   3.2 工具环境设计
   3.3 五类任务定义
   3.4 标注流程与 Ground Truth 构建

4. Evaluation Protocol
   4.1 Final Answer Evaluation
   4.2 Tool-Use Evaluation
   4.3 Spatial Grounding Evaluation
   4.4 Safety Evaluation
   4.5 Efficiency Evaluation

5. Experiments
   5.1 Baseline Models: GPT-4o, Gemini, Claude, Qwen-VL, LLaVA-Med, Surgical VLMs
   5.2 Ablation: no-tool vs tool-augmented
   5.3 Ablation: single-frame vs video
   5.4 Ablation: no-depth vs depth-tool
   5.5 Ablation: no-NDI vs NDI-GT

6. Analysis
   6.1 哪类任务最难
   6.2 Agent 是否真的会用工具
   6.3 是否存在视觉 grounding 失败
   6.4 是否容易漏报高风险
   6.5 depth/NDI 是否显著提升空间风险判断

7. Conclusion
   手术 Agent 从"看懂图像"走向"可验证辅助决策"
```

---

## 12. 实现路线图

### 工具实现三阶段策略

| 阶段 | 方式 | 说明 |
|------|------|------|
| **Phase 1: Oracle Tool** | 工具返回人工标注结果 | 简单、稳定，先验证 Agent 任务设计 |
| **Phase 2: Model Tool** | 工具由真实模型实现 | needle detector + stereo depth + SAM/MedSAM |
| **Phase 3: Hybrid Tool** | 模型 + 传感器混合 | 深度估计用模型，3D坐标用NDI，最接近最终系统 |

### 整体路线

```
Phase 1 ─────────────────────────────────────────────
  50-100 视频 clip, 300-500 Agent 任务
  任务集中在 needle tip, depth, distance, risk, grounding
  Oracle Tool 实现
  → 先做小而完整的 prototype

Phase 2 ─────────────────────────────────────────────
  扩展到多任务：phase recognition, tool-tissue relation,
  image quality issue, next action prediction, teaching feedback
  Model Tool 实现
  → 扩大任务覆盖面和评估维度

Phase 3 ─────────────────────────────────────────────
  完成论文：Oph-SurgAgent-Bench
  加入 NDI + 3D 数据
  Hybrid Tool 实现
  → 形成完整论文主线
```

---

## 13. 与现有工作的差异化

| 对比维度 | 手术 VQA (SurgVLM-Bench等) | 手术动作规划 (SAP-Bench) | **SurgAgent-Bench (我们)** |
|---------|--------------------------|------------------------|---------------------------|
| 核心问题 | "这张图里有什么？" | "下一步该做什么？" | "Agent 如何获取证据并做判断？" |
| 交互范式 | 单轮问答 | 单步预测 | 多轮工具调用 |
| 空间信息 | 2D 视觉 | 2D 视觉 | 2D + 3D + 真实尺度 (depth/NDI) |
| 评估范围 | 答案正确性 | 动作预测准确率 | 工具选择 + 参数 + 测量 + 风险 + 不确定性 |
| 安全性评估 | 无 | 无 | 有（第四层指标） |
| 可自动验证 | 部分 | 部分 | 全链路可自动验证 |

---

## 14. 项目结构

```
surgagent-bench/
├── README.md                        # 项目总览（本文件）
├── docs/
│   ├── TOOLS.md                     # 14 个工具详细定义
│   ├── EVALUATION.md                # 五层评价指标体系
│   ├── TASKS.md                     # 5 个 Task Family 详细设计
│   └── PAPER_OUTLINE.md             # 论文结构建议
├── benchmark/
│   ├── tools.py                     # 工具接口定义
│   ├── tasks.py                     # 任务定义
│   └── metrics.py                   # 评估指标实现
├── demo/
│   └── index.html                   # 可视化交互 Demo
└── .gitignore
```

---

## 15. 引用

- ToolLLM: [arXiv 2307.16789](https://arxiv.org/abs/2307.16789)
- MedAgentBench: [Stanford ML Group](https://stanfordmlgroup.github.io/projects/medagentbench/)
- Cholec80: [MLDTA Dataset](https://mldta.com/dataset/cholec80/)
- SurgMLLMBench: [arXiv 2511.21339](https://arxiv.org/abs/2511.21339)
- SAP-Bench: [arXiv 2506.07196](https://arxiv.org/abs/2506.07196)
- JIGSAWS: [PMC 8398563](https://pmc.ncbi.nlm.nih.gov/articles/PMC8398563)
- HelloAgents Ch12: [Datawhale](https://github.com/datawhalechina/hello-agents)

---

## License

MIT

## Author

Ethan (EthanCherry) — 计算机研究生，研究方向医学图像

---

> **核心主张**：当前医学 Agent benchmark 忽视手术场景，当前手术 MLLM benchmark 缺少工具增强和真实空间验证。SurgAgent-Bench 首次系统评估多模态大模型 Agent 在手术场景中的工具调用、空间感知和风险判断能力。
