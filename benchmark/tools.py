"""
SurgAgent-Bench 工具接口定义

定义 Agent 可调用的 14 个工具的函数签名和返回类型。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


# ============================================================
# 返回类型定义
# ============================================================

@dataclass
class FrameResult:
    frame_id: str
    image: str
    left_image: Optional[str] = None
    right_image: Optional[str] = None


@dataclass
class SegmentationResult:
    instrument_mask: str
    instrument_type: str  # needle, forceps, cystotome, hook, other
    confidence: float
    bbox: List[int] = field(default_factory=list)


@dataclass
class TipLocation:
    tip_xy: List[int]  # [x, y] pixel coordinates
    confidence: float
    is_visible: bool
    occlusion_status: str  # clear, partial, full


@dataclass
class TissueSegmentation:
    target: str  # eye_surface, cornea, sclera, lens, iris
    mask: str
    confidence: float
    area_pixels: int = 0


@dataclass
class DepthResult:
    depth_map: str
    unit: str  # "mm"
    valid_region: str
    confidence_map: str
    min_depth: float = 0.0
    max_depth: float = 0.0


@dataclass
class NDIPosition:
    tip_xyz_camera: List[float]  # [x, y, z] in camera coordinate
    tip_xyz_world: Optional[List[float]] = None
    unit: str = "mm"
    tracking_status: str = "valid"  # valid, interpolated, lost
    confidence: float = 0.0


@dataclass
class ProjectionResult:
    uv: List[float]  # [u, v] pixel coordinates
    reprojection_error: float  # in pixels


@dataclass
class DistanceResult:
    distance_mm: float
    nearest_surface_point: List[int]  # pixel coords
    risk_level_by_threshold: str  # safe, medium, high
    measurement_confidence: float


@dataclass
class FrameSearchResult:
    timestamps: List[str]
    event: str  # instrument_entering, needle_approaching_surface, etc.
    confidence: float


@dataclass
class ActionResult:
    action: str  # approach, contact, puncture_like, withdraw, idle
    confidence: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None


@dataclass
class SafetyRule:
    task: str
    safe_threshold_mm: float
    medium_risk_range: List[float]  # [min, max]
    high_risk_range: List[float]  # [min, max]
    note: str


@dataclass
class CaseInfo:
    case_id: str
    task_type: str
    camera: str
    calibration_available: bool
    ndi_available: bool
    clip_duration_sec: float = 0.0
    instrument_types: List[str] = field(default_factory=list)


@dataclass
class StructuredReport:
    risk_level: str
    distance_mm: float
    evidence_frame: str
    reason: str


@dataclass
class ReliabilityResult:
    reliability: str  # high, moderate, low
    main_issue: str = ""
    recommendation: str = ""


# ============================================================
# 工具函数定义
# ============================================================

class SurgAgentTools:
    """SurgAgent-Bench 核心工具集"""

    # ---- 视觉感知工具 ----

    @staticmethod
    def get_frame(video_id: str, timestamp: str) -> FrameResult:
        """从手术视频取某一时刻的图像帧。"""
        ...

    @staticmethod
    def segment_instrument(frame_id: str) -> SegmentationResult:
        """分割图像中的手术器械区域。"""
        ...

    @staticmethod
    def localize_needle_tip(frame_id: str) -> TipLocation:
        """定位 needle tip 的 2D 图像坐标。"""
        ...

    @staticmethod
    def segment_tissue(frame_id: str, target: str = "eye_surface") -> TissueSegmentation:
        """分割目标组织区域。"""
        ...

    # ---- 深度与空间测量工具 ----

    @staticmethod
    def estimate_depth(
        left_frame_id: str,
        right_frame_id: str,
        camera_params: dict
    ) -> DepthResult:
        """双目深度估计，输出 dense depth map。"""
        ...

    @staticmethod
    def query_ndi_tip_position(
        timestamp: str,
        coordinate: str = "camera"
    ) -> NDIPosition:
        """查询 NDI 记录的针尖 3D 坐标。"""
        ...

    @staticmethod
    def project_3d_to_2d(
        point_xyz_camera: List[float],
        camera_intrinsics: dict
    ) -> ProjectionResult:
        """将 NDI 3D 点投影回显微镜图像。"""
        ...

    @staticmethod
    def measure_tip_to_surface_distance(
        tip_xyz: List[float],
        surface_depth_map: str,
        tissue_mask: str
    ) -> DistanceResult:
        """计算 needle tip 到组织表面的最近距离。"""
        ...

    # ---- 视频时序工具 ----

    @staticmethod
    def find_relevant_frames(
        video_id: str,
        query: str = "needle approaching eye surface"
    ) -> FrameSearchResult:
        """从视频中检索关键帧。"""
        ...

    @staticmethod
    def recognize_surgical_action(video_clip: str) -> ActionResult:
        """识别手术视频片段中的当前动作。"""
        ...

    # ---- 规则与知识检索工具 ----

    @staticmethod
    def retrieve_safety_rule(task: str = "needle_to_eye_distance") -> SafetyRule:
        """查询 benchmark 定义的安全阈值和风险规则。"""
        ...

    @staticmethod
    def retrieve_case_info(case_id: str) -> CaseInfo:
        """读取病例/任务元数据。"""
        ...

    # ---- 结果验证与报告工具 ----

    @staticmethod
    def generate_structured_report(
        measurements: dict,
        observations: dict
    ) -> StructuredReport:
        """生成结构化手术评估报告。"""
        ...

    @staticmethod
    def check_measurement_reliability(
        depth_confidence: float,
        tip_confidence: float,
        ndi_status: str,
        occlusion_status: str = "clear"
    ) -> ReliabilityResult:
        """综合评估测量结果的可靠性。"""
        ...
