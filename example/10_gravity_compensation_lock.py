#!/usr/bin/env python3
"""reBotArm 重力补偿控制演示（末端速度锁止版）。

在基础重力补偿的基础上，加入末端速度检测：
  - 持续计算末端执行器的线速度和角速度
  - 当末端速度 ||v_ee|| < 阈值时：目标关节角度保持锁定
  - 当末端速度 ||v_ee|| > 阈值时：目标关节角度更新为当前关节角度

控制律（MIT 模式）：
    rebotarm.arm 组: 重力前馈 + MIT 位置闭环
    rebotarm.gripper 组: MIT 控制
"""
import signal
import sys
import time
from pathlib import Path

import numpy as np
import pinocchio as pin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reBotArm_control_py.actuator import RebotArm
from reBotArm_control_py.dynamics import (
    load_dynamics_model,
    compute_generalized_gravity,
    get_default_gravity,
)
from reBotArm_control_py.kinematics import load_robot_model


_running = True
_q_target: np.ndarray = None
_lock_counter = 0
_integral: np.ndarray = None

_VEL_THRESHOLD = 0.04
_W_VEL_THRESHOLD = 0.08
_EE_FRAME = "end_link"
_KP = 7.0
_KD = 0.8


def _sigint_handler(signum, frame):
    global _running
    print("\n[gravity_comp] 收到 Ctrl+C，准备停止...")
    _running = False


signal.signal(signal.SIGINT, _sigint_handler)


_model = load_robot_model()
_data = _model.createData()
_ee_frame_id = _model.getFrameId(_EE_FRAME)


def gravity_compensation_controller(r: RebotArm, dt: float) -> None:
    global _q_target, _lock_counter, _integral

    q = r.arm.get_positions()
    qd = r.arm.get_velocities()
    n = r.arm.num_joints

    tau_g = compute_generalized_gravity(q=q)

    q_error = _q_target - q

    if _integral is None:
        _integral = np.zeros(n)

    _integral += q_error * 1.0
    np.clip(_integral, -0.5, 0.5, out=_integral)

    pin.computeJointJacobians(_model, _data, q)
    pin.updateFramePlacements(_model, _data)
    J = pin.getFrameJacobian(_model, _data, _ee_frame_id, pin.ReferenceFrame.WORLD)
    v_spatial = J @ qd
    v_ee_norm = float(np.linalg.norm(v_spatial[:3]))
    w_ee_norm = float(np.linalg.norm(v_spatial[3:]))

    if v_ee_norm > _VEL_THRESHOLD or w_ee_norm > _W_VEL_THRESHOLD:
        _q_target = q.copy()
        _lock_counter = 0
        _integral *= 0.9
    else:
        _lock_counter += 1

    r.arm.send_mit(
        pos=_q_target,
        vel=np.zeros(n),
        kp=np.full(n, _KP),
        kd=np.full(n, _KD),
        tau=tau_g + _integral,
    )
    r.gripper.send_mit(r.gripper.get_positions())

    gravity_compensation_controller._counter += 1
    if gravity_compensation_controller._counter % 20 == 0:
        lock_status = "LOCKED" if _lock_counter > 0 else "UPDATE"
        print(
            f"[{gravity_compensation_controller._counter:4d}] "
            f"{lock_status}  "
            f"v={v_ee_norm:.4f}m/s  w={w_ee_norm:.4f}rad/s  "
            f"tau_g=" + "  ".join(f"{t:+.3f}" for t in tau_g) + "  N·m"
        )


gravity_compensation_controller._counter = 0


def main() -> None:
    global _q_target

    print("=" * 65)
    print("  reBotArm 重力补偿演示（末端速度锁止版）")
    print(f"  末端速度阈值: {_VEL_THRESHOLD} m/s")
    print("  预计行为: 机械臂锁止在当前位置，用力推才能改变目标角度")
    print("  Ctrl+C 停止并断开连接")
    print("=" * 65)

    dyn_model = load_dynamics_model()
    g_vec = get_default_gravity()
    print(f"\n[模型] nq={dyn_model.nq}, nv={dyn_model.nv}")
    print(f"[重力] {g_vec}  m/s²")

    rebotarm = RebotArm()
    rebotarm.connect()
    rebotarm.arm.mode_mit()
    rebotarm.gripper.mode_mit()
    rebotarm.enable_all()
    _q_target = rebotarm.arm.get_positions()
    print(f"[目标角度] 初始锁定: {np.rad2deg(_q_target).round(2)} deg")

    rebotarm.start_control_loop(gravity_compensation_controller, rate=rebotarm.rate)
    print(f"[控制循环] 启动 @ {rebotarm.rate} Hz")

    try:
        while _running:
            time.sleep(0.01)
    finally:
        print("\n[停止] 关闭控制循环...")
        rebotarm.disconnect()
        print("[完成] 已安全断开连接")


if __name__ == "__main__":
    main()
