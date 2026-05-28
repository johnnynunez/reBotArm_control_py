"""reBot-DevArm 机器人模型加载模块 — 基于 Pinocchio。

所有参数从 config/rebotarm.yaml 读取，无需修改代码。
"""

from pathlib import Path
from typing import List, Tuple

import numpy as np
import pinocchio as pin
import yaml

_config_path = Path(__file__).resolve().parents[2] / "config" / "rebotarm.yaml"
_PROJECT_ROOT = _config_path.resolve().parents[1]

_cached_config: dict | None = None


def _load_config() -> dict:
    global _cached_config
    if _cached_config is not None:
        return _cached_config
    defaults = {
        "hardware_yaml": "rebotarm_rs.yaml",
        "urdf_path": "",
        "end_effector_frame": "gripper_end",
    }
    if _config_path.exists():
        loaded = yaml.safe_load(_config_path.read_text()) or {}
        for k in defaults:
            if k in loaded:
                defaults[k] = loaded[k]
    _cached_config = defaults
    return defaults


def _resolve_urdf(urdf_path: str | None = None) -> Tuple[str, str]:
    if urdf_path is None:
        urdf_path = _load_config().get("urdf_path", "")

    if not urdf_path:
        raise ValueError("urdf_path is empty. Set urdf_path in config/rebotarm.yaml")

    if not Path(urdf_path).is_absolute():
        urdf_path = str(_PROJECT_ROOT / urdf_path)

    pkg_dir = str(Path(urdf_path).resolve().parent)
    # If the URDF lives in a "urdf/" subdirectory (common convention),
    # the meshes/ folder is typically at the package root (one level up).
    # Detect this layout and adjust pkg_dir accordingly.
    if pkg_dir.endswith("/urdf") or pkg_dir.endswith("\\urdf"):
        pkg_dir = str(Path(pkg_dir).parent)
    return urdf_path, pkg_dir


def load_robot_model(urdf_path: str | None = None) -> pin.Model:
    path, _ = _resolve_urdf(urdf_path)
    return pin.buildModelFromUrdf(path)


def get_end_effector_frame() -> str:
    return _load_config().get("end_effector_frame", "gripper_end")


def get_joint_count() -> int:
    model = load_robot_model()
    return model.nq


def get_joint_names(model: pin.Model) -> List[str]:
    return [n for n, j in zip(model.names[1:], model.joints[1:]) if j.idx_q >= 0]


def get_joint_limits(model: pin.Model) -> List[Tuple[float, float]]:
    limits = []
    for name in get_joint_names(model):
        jid = model.getJointId(name)
        lo, hi = float(model.lowerPositionLimit[jid]), float(model.upperPositionLimit[jid])
        limits.append((-np.inf, np.inf) if np.isinf(lo) and np.isinf(hi) else (lo, hi))
    return limits


def get_end_effector_frame_id(model: pin.Model) -> int:
    return model.getFrameId(get_end_effector_frame())


def get_all_frame_names(model: pin.Model) -> List[str]:
    return [f.name for f in model.frames]


def pad_q_for_model(model: pin.Model, q: np.ndarray, controlled_joints: int | None = None) -> np.ndarray:
    nq = model.nq
    n_ctrl = controlled_joints if controlled_joints is not None else nq
    if q.shape[0] >= nq:
        return q
    padded = np.zeros(nq)
    padded[:min(q.shape[0], n_ctrl)] = q[:min(q.shape[0], n_ctrl)]
    return padded
