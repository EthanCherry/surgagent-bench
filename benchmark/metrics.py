"""
SurgAgent-Bench 评估指标实现

五层评价指标体系的具体实现。
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


# ============================================================
# 第一层：任务完成指标
# ============================================================

def task_success_rate(predictions: List[Dict], ground_truth: List[Dict]) -> float:
    """任务成功率"""
    correct = sum(1 for p, g in zip(predictions, ground_truth) if _is_task_success(p, g))
    return correct / len(predictions) if predictions else 0.0


def _is_task_success(pred: Dict, gt: Dict, distance_tolerance: float = 0.2) -> bool:
    """判断单个任务是否成功"""
    distance_ok = abs(pred.get("distance_mm", 0) - gt.get("distance_mm", 0)) < distance_tolerance
    risk_ok = pred.get("risk_level") == gt.get("risk_level")
    return distance_ok and risk_ok


def risk_accuracy(predictions: List[str], ground_truth: List[str]) -> float:
    """风险等级分类正确率"""
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    return correct / len(predictions) if predictions else 0.0


def risk_f1(predictions: List[str], ground_truth: List[str], average: str = "macro") -> float:
    """风险分类 F1（多分类）"""
    from sklearn.metrics import f1_score
    return f1_score(ground_truth, predictions, average=average)


def distance_mae(predictions: List[float], ground_truth: List[float]) -> float:
    """距离估计 MAE"""
    return np.mean(np.abs(np.array(predictions) - np.array(ground_truth)))


def distance_rmse(predictions: List[float], ground_truth: List[float]) -> float:
    """距离估计 RMSE"""
    return np.sqrt(np.mean((np.array(predictions) - np.array(ground_truth)) ** 2))


# ============================================================
# 第二层：工具调用指标
# ============================================================

def tool_selection_accuracy(
    pred_tools: List[List[str]],
    gt_tools: List[List[str]]
) -> float:
    """工具选择准确率"""
    correct = 0
    total = 0
    for pt, gt in zip(pred_tools, gt_tools):
        gt_set = set(gt)
        pred_set = set(pt)
        correct += len(gt_set & pred_set)
        total += len(gt_set)
    return correct / total if total > 0 else 0.0


def tool_chain_completion(
    pred_tools: List[List[str]],
    required_chains: List[List[str]]
) -> float:
    """工具链完成率"""
    completed = 0
    for pt, rc in zip(pred_tools, required_chains):
        if all(tool in pt for tool in rc):
            completed += 1
    return completed / len(required_chains) if required_chains else 0.0


def invalid_tool_call_rate(
    pred_tools: List[List[str]],
    valid_tools: List[str]
) -> float:
    """无效工具调用率"""
    invalid = 0
    total = 0
    valid_set = set(valid_tools)
    for pt in pred_tools:
        for tool in pt:
            total += 1
            if tool not in valid_set:
                invalid += 1
    return invalid / total if total > 0 else 0.0


def tool_efficiency(pred_tool_count: List[int], optimal_count: List[int]) -> float:
    """工具调用效率（越低越好）"""
    return np.mean(np.array(pred_tool_count) / np.array(optimal_count))


# ============================================================
# 第三层：视觉与空间 Grounding 指标
# ============================================================

def tip_localization_error(
    pred_tips: List[Tuple[int, int]],
    gt_tips: List[Tuple[int, int]]
) -> float:
    """针尖定位平均欧氏距离误差"""
    errors = [np.sqrt((px - gx) ** 2 + (py - gy) ** 2)
              for (px, py), (gx, gy) in zip(pred_tips, gt_tips)]
    return np.mean(errors)


def mask_iou(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """分割 Mask IoU"""
    intersection = np.logical_and(pred_mask, gt_mask).sum()
    union = np.logical_or(pred_mask, gt_mask).sum()
    return intersection / union if union > 0 else 0.0


def mask_dice(pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
    """Dice 系数"""
    intersection = np.logical_and(pred_mask, gt_mask).sum()
    return 2 * intersection / (pred_mask.sum() + gt_mask.sum()) if (pred_mask.sum() + gt_mask.sum()) > 0 else 0.0


def temporal_grounding_error(
    pred_timestamps: List[float],
    gt_timestamps: List[float]
) -> float:
    """时序定位误差（秒）"""
    errors = [abs(p - g) for p, g in zip(pred_timestamps, gt_timestamps)]
    return np.mean(errors)


# ============================================================
# 第四层：安全性指标 🔑
# ============================================================

def critical_risk_recall(
    predictions: List[str],
    ground_truth: List[str],
    high_risk_label: str = "high"
) -> float:
    """
    高风险召回率
    在所有 GT 为 high_risk 的样本中，被正确召回的比例。
    目标值：1.0（宁肯误报，不可漏报）
    """
    high_risk_indices = [i for i, gt in enumerate(ground_truth) if gt == high_risk_label]
    if not high_risk_indices:
        return 1.0
    recalled = sum(1 for i in high_risk_indices if predictions[i] == high_risk_label)
    return recalled / len(high_risk_indices)


def false_safe_rate(
    predictions: List[str],
    ground_truth: List[str],
    safe_label: str = "safe"
) -> float:
    """
    误安全率
    在 GT 为 risky (medium/high) 的样本中，被预测为 safe 的比例。
    目标值：0.0
    """
    risky_indices = [i for i, gt in enumerate(ground_truth) if gt != safe_label]
    if not risky_indices:
        return 0.0
    false_safe = sum(1 for i in risky_indices if predictions[i] == safe_label)
    return false_safe / len(risky_indices)


def hallucinated_evidence_rate(
    pred_evidences: List[Optional[str]],
    valid_evidences: List[str]
) -> float:
    """编造证据率"""
    valid_set = set(valid_evidences)
    hallucinations = sum(1 for e in pred_evidences if e and e not in valid_set)
    return hallucinations / len(pred_evidences) if pred_evidences else 0.0


# ============================================================
# 第五层：效率与稳定性指标
# ============================================================

def repeated_run_stability(
    runs: List[List[str]]
) -> float:
    """
    多次运行一致性
    输入：多次运行的结果列表
    返回：一致运行的比例
    """
    if len(runs) < 2:
        return 1.0
    # 计算与其他运行一致的运行比例
    consistent = 0
    for i, run in enumerate(runs):
        if all(run == other for j, other in enumerate(runs) if j != i):
            consistent += 1
    return consistent / len(runs)


# ============================================================
# 综合评分
# ============================================================

def compute_final_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """计算加权总分"""
    total = 0.0
    for metric, weight in weights.items():
        if metric in scores:
            total += scores[metric] * weight
    return total


# 默认权重（Oph-SurgAgent-Bench 第一版）
DEFAULT_WEIGHTS = {
    "task_success_rate": 0.25,
    "tool_selection_accuracy": 0.25,
    "spatial_grounding": 0.20,
    "safety_score": 0.20,
    "efficiency_score": 0.10,
}
