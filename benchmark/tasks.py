"""
SurgAgent-Bench 任务定义

定义五大任务家族的具体任务模板和 ground truth 格式。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal


# ============================================================
# 任务类型
# ============================================================

TaskFamily = Literal[
    "measurement",       # Task 1: 工具调用与测量
    "scene_understanding",  # Task 2: 场景理解
    "workflow",          # Task 3: 流程推理
    "safety",            # Task 4: 安全检测
    "report",            # Task 5: 报告生成
]

RiskLevel = Literal["safe", "medium", "high"]
ActionType = Literal["approach", "contact", "puncture_like", "withdraw", "idle"]
PhaseType = Literal["preparation", "insertion", "approach", "contact", "manipulation", "withdrawal"]


# ============================================================
# 任务输入定义
# ============================================================

@dataclass
class TaskInput:
    """Agent 任务输入"""
    case_id: str
    task_type: TaskFamily
    task_instruction: str                    # 自然语言任务描述
    input_type: str = "video_clip"           # video_clip / image / image_pair
    video_clip: Optional[str] = None         # 视频路径
    image: Optional[str] = None              # 单帧图像路径
    left_image: Optional[str] = None         # 双目左图
    right_image: Optional[str] = None        # 双目右图
    available_tools: List[str] = field(default_factory=list)
    camera_params: Optional[dict] = None     # 相机参数
    metadata: dict = field(default_factory=dict)


# ============================================================
# Agent 预期输出
# ============================================================

@dataclass
class AgentOutput:
    """Agent 预期输出格式"""
    case_id: str
    task_type: TaskFamily
    # 核心判断
    answer: str = ""
    risk_level: Optional[RiskLevel] = None
    # 证据
    evidence_timestamp: Optional[str] = None
    evidence_frame: Optional[str] = None
    needle_tip_xy: Optional[List[int]] = None  # 针尖 2D 坐标
    target_region: Optional[str] = None        # 目标组织区域
    # 测量值
    distance_mm: Optional[float] = None
    phase: Optional[PhaseType] = None
    action: Optional[ActionType] = None
    # 工具调用记录
    tool_calls: List[str] = field(default_factory=list)
    # 不确定性
    uncertainty: str = ""   # high / moderate / low
    reliability_issues: List[str] = field(default_factory=list)
    reason: str = ""


# ============================================================
# Ground Truth
# ============================================================

@dataclass
class GroundTruth:
    """任务 Ground Truth"""
    case_id: str
    task_type: TaskFamily
    # 核心答案
    risk_level: Optional[RiskLevel] = None
    distance_mm: Optional[float] = None
    acceptable_error_mm: float = 0.2
    # 空间 GT
    needle_tip_xy: Optional[List[int]] = None
    target_region_mask: Optional[str] = None
    instrument_mask: Optional[str] = None
    # 时序 GT
    evidence_timestamp_range: Optional[List[str]] = None  # [start, end]
    phase: Optional[PhaseType] = None
    action: Optional[ActionType] = None
    # 必需工具链
    required_tools: List[str] = field(default_factory=list)
    optimal_tool_count: int = 0
    # 安全 GT
    safety_risks: List[str] = field(default_factory=list)
    # 元数据
    difficulty: str = "medium"  # easy / medium / hard


# ============================================================
# 任务样例
# ============================================================

SAMPLE_TASKS = [
    # ---- Task 1: Tool-use / Measurement ----
    {
        "input": TaskInput(
            case_id="pigeye_001",
            task_type="measurement",
            task_instruction="判断当前针尖到眼表的距离是否处于风险范围，并给出证据帧、针尖坐标、距离值和风险等级。",
            video_clip="pigeye_001.mp4",
            available_tools=[
                "get_frame", "localize_needle_tip", "segment_tissue",
                "estimate_depth", "query_ndi_tip_position",
                "measure_tip_to_surface_distance", "retrieve_safety_rule"
            ],
        ),
        "gt": GroundTruth(
            case_id="pigeye_001",
            task_type="measurement",
            risk_level="medium",
            distance_mm=0.79,
            acceptable_error_mm=0.2,
            needle_tip_xy=[608, 386],
            evidence_timestamp_range=["00:07.0", "00:07.5"],
            required_tools=["get_frame", "localize_needle_tip", "segment_tissue",
                          "estimate_depth", "measure_tip_to_surface_distance",
                          "retrieve_safety_rule"],
            optimal_tool_count=6,
            difficulty="easy",
        ),
    },
    # ---- Task 2: Scene Understanding ----
    {
        "input": TaskInput(
            case_id="pigeye_002",
            task_type="scene_understanding",
            task_instruction="分析当前画面中的器械类型、可见组织区域、器械-组织接触关系以及图像质量问题。",
            video_clip="pigeye_002.mp4",
            available_tools=[
                "get_frame", "segment_instrument", "segment_tissue",
                "localize_needle_tip"
            ],
        ),
        "gt": GroundTruth(
            case_id="pigeye_002",
            task_type="scene_understanding",
            needle_tip_xy=[612, 384],
            required_tools=["get_frame", "segment_instrument", "segment_tissue"],
            optimal_tool_count=3,
            difficulty="easy",
        ),
    },
    # ---- Task 3: Workflow ----
    {
        "input": TaskInput(
            case_id="pigeye_003",
            task_type="workflow",
            task_instruction="判断当前手术处于哪个阶段（视野建立/器械进入/靠近眼表/接触定位/操作执行/器械退出），并预测下一个阶段。",
            video_clip="pigeye_003.mp4",
            available_tools=[
                "get_frame", "find_relevant_frames",
                "recognize_surgical_action", "retrieve_case_info"
            ],
        ),
        "gt": GroundTruth(
            case_id="pigeye_003",
            task_type="workflow",
            phase="approach",
            action="approach",
            required_tools=["get_frame", "find_relevant_frames", "recognize_surgical_action"],
            optimal_tool_count=3,
            difficulty="medium",
        ),
    },
    # ---- Task 4: Safety ----
    {
        "input": TaskInput(
            case_id="pigeye_004",
            task_type="safety",
            task_instruction="评估当前手术场景的安全风险：是否存在距离过近、遮挡、反光、NDI追踪异常等问题。如果信息不足，请标注不确定性。",
            video_clip="pigeye_004.mp4",
            available_tools=[
                "get_frame", "localize_needle_tip", "segment_tissue",
                "estimate_depth", "query_ndi_tip_position",
                "measure_tip_to_surface_distance", "retrieve_safety_rule",
                "check_measurement_reliability"
            ],
        ),
        "gt": GroundTruth(
            case_id="pigeye_004",
            task_type="safety",
            risk_level="high",
            distance_mm=0.35,
            safety_risks=["distance_too_close", "specular_reflection"],
            required_tools=["get_frame", "estimate_depth", "measure_tip_to_surface_distance",
                          "retrieve_safety_rule", "check_measurement_reliability"],
            optimal_tool_count=5,
            difficulty="hard",
        ),
    },
    # ---- Task 5: Report ----
    {
        "input": TaskInput(
            case_id="pigeye_005",
            task_type="report",
            task_instruction="观察这段训练视频，生成结构化教学反馈：评价器械稳定性、目标区域接近效率、是否存在不必要移动、关键步骤是否完成。",
            video_clip="pigeye_005.mp4",
            available_tools=[
                "get_frame", "find_relevant_frames", "recognize_surgical_action",
                "localize_needle_tip", "retrieve_case_info",
                "generate_structured_report"
            ],
        ),
        "gt": GroundTruth(
            case_id="pigeye_005",
            task_type="report",
            required_tools=["get_frame", "recognize_surgical_action"],
            optimal_tool_count=4,
            difficulty="medium",
        ),
    },
]
