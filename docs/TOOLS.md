# SurgAgent-Bench 工具环境详细定义

## 概述

SurgAgent-Bench 中的"工具"是一组可调用的函数/API，Agent 通过调用这些工具获取手术场景中的证据信息，而非直接依赖大模型"看图猜答案"。

**核心设计原则**：
> Agent = 大模型大脑
> 工具 = 外部感知/测量/检索/计算模块
> Benchmark = 评估 Agent 是否正确选择工具、传入参数、读取结果、做出判断

---

## 工具分类总览

| 类别 | 工具数量 | 作用 |
|------|---------|------|
| 视觉感知工具 | 4 | 从图像/视频提取基础视觉信息 |
| 深度与空间测量工具 | 4 | 进行深度估计和3D空间测量 |
| 视频时序工具 | 2 | 处理视频时间维度 |
| 规则与知识检索工具 | 2 | 查询手术知识和任务规则 |
| 结果验证与报告工具 | 2 | 结构化输出和可靠性检查 |
| **合计** | **14** | |

---

## 一、视觉感知工具

### 1. get_frame

```python
def get_frame(video_id: str, timestamp: str) -> FrameResult:
    """
    从手术视频中取某一时刻的图像帧。

    Args:
        video_id: 视频标识符，如 "pigeye_001"
        timestamp: 时间戳，格式 "MM:SS.s"，如 "00:07.2"

    Returns:
        FrameResult {
            frame_id: str,       # 帧标识符
            image: str,          # 帧图像路径
            left_image: str,     # 左目图像（双目时）
            right_image: str     # 右目图像（双目时）
        }
    """
```

**评估关注点**：Agent 是否能正确定位关键时间点。

---

### 2. segment_instrument

```python
def segment_instrument(frame_id: str) -> SegmentationResult:
    """
    分割图像中的手术器械区域。

    Args:
        frame_id: 帧标识符

    Returns:
        SegmentationResult {
            instrument_mask: str,   # 器械分割 mask 路径
            instrument_type: str,   # 器械类型：needle/forceps/cystotome/hook
            confidence: float,      # 置信度 [0, 1]
            bbox: list              # 边界框 [x, y, w, h]
        }
    """
```

**支持的器械类型**：
- `needle` - 手术针
- `forceps` - 镊子
- `cystotome` - 截囊针
- `hook` - 钩子
- `other` - 其他

---

### 3. localize_needle_tip

```python
def localize_needle_tip(frame_id: str) -> TipLocation:
    """
    定位 needle tip 的 2D 图像坐标。

    Args:
        frame_id: 帧标识符

    Returns:
        TipLocation {
            tip_xy: list,        # [x, y] 像素坐标
            confidence: float,   # 置信度 [0, 1]
            is_visible: bool,    # 针尖是否可见
            occlusion_status: str # 遮挡状态：clear/partial/full
        }
    """
```

**评估关注点**：针尖定位误差、可见性判断。

---

### 4. segment_tissue

```python
def segment_tissue(frame_id: str, target: str = "eye_surface") -> TissueSegmentation:
    """
    分割目标组织区域。

    Args:
        frame_id: 帧标识符
        target: 目标组织类型

    Returns:
        TissueSegmentation {
            target: str,          # 组织类型
            mask: str,            # 分割 mask 路径
            confidence: float,    # 置信度 [0, 1]
            area_pixels: int      # 区域面积（像素）
        }
    """
```

**支持的组织类型**：
- `eye_surface` - 眼表
- `cornea` - 角膜
- `sclera` - 巩膜
- `lens` - 晶状体
- `iris` - 虹膜

---

## 二、深度与空间测量工具

### 5. estimate_depth

```python
def estimate_depth(
    left_frame_id: str,
    right_frame_id: str,
    camera_params: dict
) -> DepthResult:
    """
    双目深度估计，输出 dense depth map。

    Args:
        left_frame_id: 左目帧标识符
        right_frame_id: 右目帧标识符
        camera_params: 相机参数（内参 + 基线）

    Returns:
        DepthResult {
            depth_map: str,            # 深度图路径 (.npy)
            unit: str,                 # 单位："mm"
            valid_region: str,         # 有效区域 mask
            confidence_map: str,       # 置信度图
            min_depth: float,          # 最小深度
            max_depth: float           # 最大深度
        }
    """
```

**评估关注点**：Agent 是否知道何时需要深度信息，而非靠肉眼估计。

---

### 6. query_ndi_tip_position

```python
def query_ndi_tip_position(
    timestamp: str,
    coordinate: str = "camera"
) -> NDIPosition:
    """
    查询 NDI 记录的针尖 3D 坐标。

    Args:
        timestamp: 时间戳
        coordinate: 坐标系统，"camera" 或 "world"

    Returns:
        NDIPosition {
            tip_xyz_camera: list,    # 相机坐标系下的 3D 坐标 [x, y, z]
            tip_xyz_world: list,     # 世界坐标系下的 3D 坐标
            unit: str,               # "mm"
            tracking_status: str,    # "valid" / "interpolated" / "lost"
            confidence: float        # 追踪置信度
        }
    """
```

---

### 7. project_3d_to_2d

```python
def project_3d_to_2d(
    point_xyz_camera: list,
    camera_intrinsics: dict
) -> ProjectionResult:
    """
    将 3D 相机坐标点投影到 2D 图像平面。

    Args:
        point_xyz_camera: 相机坐标系下的 3D 点
        camera_intrinsics: 相机内参矩阵

    Returns:
        ProjectionResult {
            uv: list,                # [u, v] 像素坐标
            reprojection_error: float # 重投影误差 (pixels)
        }
    """
```

**用途**：验证 NDI 针尖位置与图像中针尖是否一致。

---

### 8. measure_tip_to_surface_distance ⭐ 核心工具

```python
def measure_tip_to_surface_distance(
    tip_xyz: list,
    surface_depth_map: str,
    tissue_mask: str
) -> DistanceResult:
    """
    计算 needle tip 到组织表面的最近距离。

    这是 SurgAgent-Bench 最核心的测量工具，整合了：
    针尖定位 + 组织分割 + 深度图 + 3D 坐标

    Args:
        tip_xyz: 针尖 3D 坐标（相机坐标系）
        surface_depth_map: 组织表面深度图路径
        tissue_mask: 组织区域 mask 路径

    Returns:
        DistanceResult {
            distance_mm: float,              # 最近距离 (mm)
            nearest_surface_point: list,     # 表面最近点像素坐标
            risk_level_by_threshold: str,    # 按阈值判定的风险等级
            measurement_confidence: float    # 测量置信度
        }
    """
```

---

## 三、视频时序工具

### 9. find_relevant_frames

```python
def find_relevant_frames(
    video_id: str,
    query: str = "needle approaching eye surface"
) -> FrameSearchResult:
    """
    根据自然语言查询从视频中检索关键帧。

    Args:
        video_id: 视频标识符
        query: 自然语言事件描述

    Returns:
        FrameSearchResult {
            timestamps: list,    # 相关时刻列表
            event: str,          # 识别到的事件类型
            confidence: float    # 检索置信度
        }
    """
```

**支持的事件类型**：
- `instrument_entering` - 器械进入
- `needle_approaching_surface` - 针尖靠近组织
- `needle_contact` - 针尖接触
- `instrument_withdrawing` - 器械退出

---

### 10. recognize_surgical_action

```python
def recognize_surgical_action(video_clip: str) -> ActionResult:
    """
    识别手术视频片段中的当前动作。

    Args:
        video_clip: 视频片段标识符

    Returns:
        ActionResult {
            action: str,        # 动作类型
            confidence: float,  # 置信度
            start_time: str,    # 动作开始时间
            end_time: str       # 动作结束时间
        }
    """
```

**支持的动作类型**：
- `approach` - 靠近
- `contact` - 接触
- `puncture_like` - 穿刺类动作
- `withdraw` - 退出
- `idle` - 静止

---

## 四、规则与知识检索工具

### 11. retrieve_safety_rule

```python
def retrieve_safety_rule(task: str = "needle_to_eye_distance") -> SafetyRule:
    """
    查询 benchmark 定义的安全阈值和风险规则。

    Args:
        task: 任务类型标识

    Returns:
        SafetyRule {
            task: str,
            safe_threshold_mm: float,          # 安全距离阈值
            medium_risk_range: list,           # 中风险范围 [min, max]
            high_risk_range: list,             # 高风险范围 [min, max]
            note: str                          # 免责说明
        }
    """
```

**当前定义的规则**：

| 距离范围 | 风险等级 |
|---------|---------|
| > 1.0 mm | safe |
| 0.5 - 1.0 mm | medium risk |
| < 0.5 mm | high risk |

> ⚠️ 以上阈值仅为 benchmark 评估使用，不代表临床标准。

---

### 12. retrieve_case_info

```python
def retrieve_case_info(case_id: str) -> CaseInfo:
    """
    读取病例/任务元数据。

    Args:
        case_id: 病例标识符

    Returns:
        CaseInfo {
            case_id: str,
            task_type: str,             # 任务类型
            camera: str,                # 相机类型
            calibration_available: bool, # 标定是否可用
            ndi_available: bool,        # NDI 数据是否可用
            clip_duration_sec: float,   # 视频时长
            instrument_types: list      # 出现的器械类型
        }
    """
```

---

## 五、结果验证与报告工具

### 13. generate_structured_report

```python
def generate_structured_report(
    measurements: dict,
    observations: dict
) -> StructuredReport:
    """
    生成结构化手术评估报告。

    Args:
        measurements: 测量结果字典
        observations: 观察记录字典

    Returns:
        StructuredReport {
            risk_level: str,
            distance_mm: float,
            evidence_frame: str,
            reason: str
        }
    """
```

---

### 14. check_measurement_reliability

```python
def check_measurement_reliability(
    depth_confidence: float,
    tip_confidence: float,
    ndi_status: str,
    occlusion_status: str = "clear"
) -> ReliabilityResult:
    """
    综合评估测量结果的可靠性。

    Args:
        depth_confidence: 深度估计置信度
        tip_confidence: 针尖定位置信度
        ndi_status: NDI 追踪状态
        occlusion_status: 遮挡状态

    Returns:
        ReliabilityResult {
            reliability: str,     # "high" / "moderate" / "low"
            main_issue: str,      # 主要可靠性问题（如有）
            recommendation: str   # 建议操作
        }
    """
```

---

## 核心 8 工具（推荐起步）

初期建议先实现 8 个核心工具：

| # | 工具 | 分类 |
|---|------|------|
| 1 | `get_frame` | 视觉感知 |
| 2 | `localize_needle_tip` | 视觉感知 |
| 3 | `segment_instrument` | 视觉感知 |
| 4 | `segment_eye_surface` | 视觉感知 |
| 5 | `estimate_depth` | 深度测量 |
| 6 | `query_ndi_tip_position` | 深度测量 |
| 7 | `measure_tip_to_surface_distance` | 深度测量 |
| 8 | `retrieve_safety_rule` | 知识检索 |

---

## 工具实现三阶段

| 阶段 | 方式 | 说明 |
|------|------|------|
| **Phase 1: Oracle** | 返回人工标注的 GT 结果 | 验证 Agent 任务设计，排除工具误差 |
| **Phase 2: Model** | 真实模型实现 | needle detector + stereo depth + SAM/MedSAM |
| **Phase 3: Hybrid** | 模型 + 传感器 | 深度模型 + NDI 真实数据，最接近最终系统 |

---

## 工具调用评估标准

| 评估维度 | 说明 |
|---------|------|
| Tool Selection Accuracy | Agent 是否选了正确的工具 |
| Parameter Accuracy | 参数是否正确（timestamp, ROI, target） |
| Call Sequence Correctness | 调用顺序是否符合任务逻辑 |
| Completeness | 是否调用了所有必要工具 |
| Efficiency | 是否存在冗余调用 |
