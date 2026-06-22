# reBot Arm B601-DM Pinocchio & MeshCat Getting Started Guide

<p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg" alt="Platform">
    <img src="https://img.shields.io/badge/Framework-Pinocchio-yellow.svg" alt="Pinocchio">
</p>

<p align="center"><strong>6-DOF Robotic Arm · Multi-Motor · Kinematics · Trajectory Planning · MIT License</strong></p>

<p align="center">
    <a href="./README_zh.md">简体中文</a> &nbsp;|&nbsp;
    <a href="./README.md">English</a> &nbsp;|&nbsp;
    <a href="./README_JP.md">日本語</a>&nbsp;|&nbsp;
    <a href="./README_Fr.md">français</a>&nbsp;|&nbsp;
    <a href="./README_es.md">Español</a>
</p>

---

## 📖 Introduction

**reBotArm Control**: Python library for reBot Arm B601 series — motor control, kinematics, trajectory planning.

- 🦾 Dual models: B601-DM (Damiao) / B601-RS (RobStride)
- 🧮 Kinematics: FK/IK via Pinocchio
- 🛤️ Trajectory: SE(3) geodesic + CLIK tracking
- 🔧 Config: YAML-driven

---

## ⚙️ Installation (Linux / Windows)

### 1. Install Anaconda / Miniconda
Download [Miniconda](https://docs.conda.io/en/latest/miniconda.html). Windows users open **Anaconda PowerShell Prompt** (not regular PowerShell).

### 2. Create env + install dependencies
```bash
conda create -n robotarm python=3.10 -y
conda activate robotarm
git clone https://github.com/vectorBH6/reBotArm_control_py.git
cd reBotArm_control_py
pip install -e .
pip install motorbridge
```

> Do NOT use the project's `.venv/`. Always `conda activate robotarm` first.

### 3. Verify
```bash
motorbridge-cli scan --vendor robstride --channel can0@1000000 --start-id 1 --end-id 5
```
You should see 5 motors (adjust count to your hardware).

---

## 🪟 Windows: PEAK PCAN-USB

On Windows, `motorbridge` uses PCAN-Basic to communicate with PCAN-USB adapters.

| Item | What to do |
|---|---|
| **Driver** | Download PCAN-Driver from https://www.peak-system.com/quick-drivers (includes `PCANBasic.dll` + PCAN-View) |
| **Verify DLL** | `Test-Path C:\Windows\System32\PCANBasic.dll` → `True` |
| **Channel naming** | `can0` / `can1` → `PCAN_USBBUS1` / `PCAN_USBBUS2`; `can0@1000000` = 1 Mbps |
| **Default baudrates** | RS06 = 1 Mbps; RS00 / Damiao = 500 kbps |
| **Edit config** | Set `channel: can0@1000000` in `config/rebotarm_rs.yaml` (`rate` = control loop Hz, not CAN baudrate) |
| **YAML encoding** | Windows defaults to GBK, which breaks YAML files with Chinese comments. `rebotarm.py` already uses `encoding="utf-8"` — no manual fix needed. |
| **Permissions** | No `chmod` needed; allow motorbridge in Defender / 360 if prompted |
| **VM / WSL2** | PCAN-USB must be passed through to the Windows host; not usable inside VMs directly |

### Windows Troubleshooting
| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: motorbridge` | Wrong Python env → `conda activate robotarm` |
| `UnicodeDecodeError: 'gbk'` | See YAML encoding row above |
| Scan returns nothing | Try a different baudrate (`@500000` ↔ `@1000000`); check with PCAN-View |
| Motor not responding | Check 120Ω termination resistors; verify `motor_id` matches scan |

---

## 🔌 Hardware Configuration

| Motor | Platform | Transport | Channel / Port | Baudrate |
|---|---|---|---|---|
| Damiao | Linux | Serial Bridge | `/dev/ttyACM0` | 921600 |
| Damiao | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS00 | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS06 | Linux/Windows | SocketCAN / PCAN | `can0@1000000` | 1 Mbps |

Linux SocketCAN:
```bash
sudo ip link set can0 up type can bitrate 1000000
```

Damiao serial bridge requires `--transport dm-serial`. Feedback ID rule: `feedback_id = motor_id + 0x10`.

---

## 📁 Project Structure

```
reBotArm_control_py/
├── config/                 # YAML config
├── example/                # Examples (numbered 0x01…9)
├── reBotArm_control_py/    # Core (actuator / kinematics / controllers / trajectory)
└── urdf/                   # URDF model
```

---

## 🎮 Example Programs

Always run with `conda activate robotarm` first.

| # | File | Description |
|---|---|---|
| 0x01 | `0x01rs06_test.py` / `0x01damiao_test.py` | Single motor console (`ping` / `enable` / `mode mit` / `mit <pos>`) |
| 2 | `2_zero_and_read.py` | Zero calibration + real-time angles |
| 3 | `3_mit_control.py` | MIT mode (position + velocity + torque) |
| 4 | `4_pos_vel_control.py` | POS_VEL mode |
| 5 | `5_fk_test.py` | FK: 6 joint angles (deg) → end-effector pose |
| 6 | `6_ik_test.py` | IK: end-effector pose → joint angles |
| 7 | `7_arm_ik_control.py` | Real-time IK control (`x y z [r p y]`) |
| 8 | `8_arm_traj_control.py` | SE(3) geodesic + CLIK (`x y z [r p y] [duration]`) |
| 9 | `9_gravity_compensation.py` | Gravity compensation via Pinocchio (`tau = g(q)`, kp=2 kd=1) |

**Permissions**: Linux real-machine control → `sudo chmod 666 /dev/ttyACM0` or `/dev/can0` first; Windows → no chmod needed.

---

## 📄 License

MIT

---

## ☎ Contact

- Issues: https://github.com/vectorBH6/reBotArm_control_py/issues
- Repo: https://github.com/vectorBH6/reBotArm_control_py
