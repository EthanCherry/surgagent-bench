# SurgAgent-Bench 论文结构建议

## 标题备选

1. **SurgAgent-Bench: Benchmarking Multimodal LLM Agents for Tool-Augmented Surgical Scene Understanding and Risk Assessment**

2. **Oph-SurgAgent-Bench: A Tool-Augmented Multimodal Agent Benchmark for Spatial Perception and Risk Assessment in Ophthalmic Microsurgery**

---

## 论文大纲

### 1. Introduction

**核心论点**：
- 医学 LLM benchmark 已从静态 QA 发展到临床 Agent（MedAgentBench, AgentClinic）
- 手术 AI benchmark 已覆盖 phase recognition, tool detection, VQA, action planning
- **但缺少专门评估"手术场景下 Agent 感知→调用工具→推理→决策"完整链路的 benchmark**
- 手术 Agent 需要：多模态感知 + 工具调用 + 空间测量 + 风险判断
- 因此提出 SurgAgent-Bench / Oph-SurgAgent-Bench

**Contributions**：
1. 首次提出面向手术场景的多模态 Agent benchmark
2. 设计 14 个工具接口和 5 类任务，覆盖感知、测量、推理、安全
3. 建立五层评价体系，特别是安全性和空间 grounding 指标
4. 开源 benchmark 框架和基线实验

---

### 2. Related Work

#### 2.1 General LLM Agent Benchmarks
- GAIA (Mialon et al., 2023): 466 个多步推理问题
- AgentBench (Liu et al., 2023): 8 类交互环境
- ToolBench / ToolLLM (Qin et al., 2023): 16,464 API
- WebArena (Zhou et al., 2023): 812 网页任务
- OSWorld (Xie et al., 2024): 369 真实电脑任务
- SWE-bench (Jimenez et al., 2023): 自动验证的代码修复任务
- **BFCL**: AST 匹配评估函数调用

#### 2.2 Medical LLM / Agent Benchmarks
- MedHELM: 临床决策、病历、患者沟通
- MedS-Bench: 11 类临床任务
- **MedAgentBench**: FHIR EHR 环境中的 300 个临床 Agent 任务
- **AgentClinic**: 模拟临床环境，患者交互 + 工具使用
- MedAgentsBench: 复杂医学推理和诊断规划

#### 2.3 Surgical AI Benchmarks
- Cholec80: 胆囊切除术 phase + tool
- EndoVis Challenge: 器械/场景分割
- JIGSAWS: 机器人手术技能评估
- SurgBench: 72 个手术视频任务
- SurgMLLMBench: 手术多模态理解
- **SAP-Bench**: 手术动作规划

---

### 3. SurgAgent-Bench Construction

#### 3.1 数据来源
- 公开手术视频数据集（Cholec80, JIGSAWS 等）
- 自有显微镜双目视频数据（猪眼前节实验）
- NDI 追踪数据（3D 坐标 ground truth）

#### 3.2 工具环境设计
- 14 个工具，5 大类（视觉感知、深度测量、时序、知识检索、验证报告）
- 三阶段实现（Oracle → Model → Hybrid）
- 工具调用协议和返回格式

#### 3.3 五类任务设计
- Task 1: Tool-use / Measurement（核心）
- Task 2: Scene Understanding
- Task 3: Workflow / Phase Reasoning
- Task 4: Safety / Risk Detection
- Task 5: Report / Teaching Feedback

#### 3.4 标注流程与 Ground Truth
- 人工标注：针尖坐标、组织mask、风险等级
- NDI：3D 坐标 ground truth
- 双人标注 + 交叉验证
- 标注一致性评估 (Cohen's Kappa, IoU)

---

### 4. Evaluation Protocol

#### 4.1 Task Completion (L1)
- Task Success Rate, Risk F1, Distance MAE/RMSE, Phase Accuracy

#### 4.2 Tool Usage (L2)
- Tool Selection Accuracy, AST Match, Chain Completion, Efficiency

#### 4.3 Spatial Grounding (L3)
- Tip Localization Error, Mask IoU/Dice, Temporal Grounding Error, Depth Error

#### 4.4 Safety (L4) 🔑
- Critical Risk Recall, False Safe Rate, Uncertainty Calibration, Hallucination Rate

#### 4.5 Efficiency & Stability (L5)
- Token Cost, Latency, Repeated-run Stability, Robustness to Perturbations

---

### 5. Experiments

#### 5.1 Baselines
- GPT-4o / GPT-4V
- Gemini 2.0 Flash / Pro
- Claude 3.5 Sonnet / Opus
- Qwen-VL-Max
- LLaVA-Med
- Surgical VLMs (SurgVLM 等)

#### 5.2 Ablation Studies
- **Tool Ablation**: no-tool (纯视觉) vs tool-augmented
- **Modality Ablation**: single-frame vs video
- **Depth Ablation**: no-depth vs depth-tool
- **NDI Ablation**: no-NDI vs NDI-GT
- **Oracle vs Model Tool**: 工具误差影响分析

#### 5.3 实验设置
- 温度参数、prompt 模板、few-shot 设置
- 评估环境和计算资源

---

### 6. Analysis

#### 6.1 哪类任务最难？
- Tool-use measurement > Scene understanding > Safety > Phase > Report
- 分析：多工具协调 vs 单工具任务

#### 6.2 Agent 是否真的会用工具？
- 无效调用率分析
- 工具选择错误模式
- 是否跳过关键工具

#### 6.3 视觉 Grounding 失败模式
- 针尖定位误差分析
- 反光/遮挡对 grounding 的影响
- 时序定位误差分布

#### 6.4 安全关键错误分析
- False Safe Rate 按场景细分
- 哪些场景最容易被误判为安全
- Uncertainty 声明与实际准确率的关系

#### 6.5 Depth/NDI 的贡献
- 有无 depth/NDI 时距离估计精度对比
- 深度信息在风险判断中的作用

---

### 7. Conclusion

- 提出首个面向手术场景的多模态 Agent benchmark
- 设计了工具环境、任务体系和五层评价指标
- 实验揭示当前 MLLM 在手术 Agent 任务中的不足
- 手术 Agent 从"看懂图像"走向"可验证辅助决策"

---

### 8. Future Work

- 扩展到更多手术类型（腹腔镜、骨科、神经外科等）
- 集成真实手术机器人 API
- 多 Agent 协作的手术场景
- 临床部署和验证

---

## 关键引用

```bibtex
@article{qin2023toolllm,
  title={ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs},
  author={Qin, Yujia and others},
  journal={arXiv preprint arXiv:2307.16789},
  year={2023}
}

@article{shi2024medagentbench,
  title={MedAgentBench: A Realistic Virtual EHR Environment to Benchmark Medical LLM Agents},
  author={Shi, Wenqi and others},
  year={2024}
}

@article{wang2025sapbench,
  title={SAP-Bench: Benchmarking Multimodal Large Language Models in Surgical Action Planning},
  author={Wang, Yihao and others},
  journal={arXiv preprint arXiv:2506.07196},
  year={2025}
}
```
