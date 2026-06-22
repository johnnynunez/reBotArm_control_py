# reBot Arm B601-DM 的 Pinocchio 与 MeshCat 入门指南

<p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg" alt="Platform">
    <img src="https://img.shields.io/badge/Framework-Pinocchio-yellow.svg" alt="Pinocchio">
</p>

<p align="center"><strong>6 自由度机械臂 · 多电机支持 · 运动学求解 · 轨迹规划 · MIT 开源</strong></p>

---

## 📖 简介

**reBotArm Control**：reBot Arm B601 系列机械臂的 Python 控制库，覆盖底层电机控制 → 运动学 → 轨迹规划。

- 🦾 双型号：B601-DM（达妙）/ B601-RS（灵足）
- 🧮 运动学：基于 Pinocchio 的 FK / IK
- 🛤️ 轨迹：SE(3) 测地线 + CLIK 跟踪
- 🔧 配置：YAML 驱动

---

## ⚙️ 安装（Linux / Windows 通用）

### 1. 装 Anaconda / Miniconda
下载 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)。Windows 用户打开 **Anaconda PowerShell Prompt**（不是普通 PowerShell）。

### 2. 建环境 + 装依赖
```bash
conda create -n robotarm python=3.10 -y
conda activate robotarm
git clone https://github.com/vectorBH6/reBotArm_control_py.git
cd reBotArm_control_py
pip install -e .
pip install motorbridge
```

> 不要用项目自带的 `.venv/`。所有命令必须先 `conda activate robotarm`。

### 3. 验证
```bash
motorbridge-cli scan --vendor robstride --channel can0@1000000 --start-id 1 --end-id 5
```
能看到 5 个电机就算通。

---

## 🪟 Windows 特别说明（PEAK PCAN-USB）

Windows 下 `motorbridge` 通过 PCAN-Basic 操作 PCAN-USB。

| 项 | 做法 |
|---|---|
| **装驱动** | https://www.peak-system.com/fileadmin/media/files/PEAK-System_Driver-Setup.zip 下载 PCAN-Driver（自带 `PCANBasic.dll` + PCAN-View） |
| **验证 DLL** | `Test-Path C:\Windows\System32\PCANBasic.dll` 应返回 `True` |
| **通道名** | `can0` / `can1` 自动映射到 `PCAN_USBBUS1` / `PCAN_USBBUS2`；`can0@1000000` 表示 1 Mbps |
| **电机默认波特率** | RS06 = 1 Mbps；RS00 / 达妙 = 500 kbps |
| **改配置** | `config/rebotarm_rs.yaml` 里 `channel: can0@1000000`（`rate` 是控制循环 Hz，别搞混） |
| **YAML 中文注释** | Windows 默认 GBK 会报 `UnicodeDecodeError`。本仓库 `rebotarm.py` 已用 `encoding="utf-8"`，无需手动改 |
| **权限** | 不需要 `chmod`；Defender / 360 首次拦截放行即可 |
| **VM / WSL2** | 必须把 PCAN-USB 透传到 Windows 主机 |

### Windows 常见问题
| 症状 | 解决 |
|---|---|
| `ModuleNotFoundError: motorbridge` | 没在 conda env 里 → `conda activate robotarm` |
| `UnicodeDecodeError: 'gbk'` | 见上表 |
| scan 无响应 | 换波特率（`@500000` ↔ `@1000000`） / 用 PCAN-View 看帧 |
| 电机不回包 | 检查 120Ω 终端电阻、`motor_id` 是否跟 scan 匹配 |

---

## 🔌 硬件配置

| 电机 | 平台 | 传输 | 通道/串口 | 波特率 |
|---|---|---|---|---|
| 达妙 | Linux | 串口桥 | `/dev/ttyACM0` | 921600 |
| 达妙 | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS00 | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS06 | Linux/Windows | SocketCAN / PCAN | `can0@1000000` | 1 Mbps |

Linux SocketCAN 启动：
```bash
sudo ip link set can0 up type can bitrate 1000000
```

达妙串口桥必须加 `--transport dm-serial`。反馈 ID 规则：`feedback_id = motor_id + 0x10`。

---

## 📁 项目结构

```
reBotArm_control_py/
├── config/                 # YAML 配置
├── example/                # 示例（按 0x01…9 编号）
├── reBotArm_control_py/    # 核心库（actuator / kinematics / controllers / trajectory）
└── urdf/                   # URDF 模型
```

---

## 🎮 示例程序

跑前先 `conda activate robotarm`。

| # | 文件 | 说明 |
|---|---|---|
| 0x01 | `0x01rs06_test.py` / `0x01damiao_test.py` | 单电机交互测试（`ping` / `enable` / `mode mit` / `mit <pos>`） |
| 2 | `2_zero_and_read.py` | 零点校准 + 实时角度 |
| 3 | `3_mit_control.py` | MIT 模式（位置 + 速度 + 扭矩） |
| 4 | `4_pos_vel_control.py` | POS_VEL 模式 |
| 5 | `5_fk_test.py` | 正运动学：输入 6 个关节角（度）→ 末端位姿 |
| 6 | `6_ik_test.py` | 逆运动学：输入末端位姿 → 关节角 |
| 7 | `7_arm_ik_control.py` | IK 实时控制（`x y z [r p y]`） |
| 8 | `8_arm_traj_control.py` | SE(3) 测地线轨迹 + CLIK（`x y z [r p y] [duration]`） |
| 9 | `9_gravity_compensation.py` | 重力补偿（Pinocchio `tau = g(q)`，kp=2 kd=1） |

**权限**：Linux 实机控制前 `sudo chmod 666 /dev/ttyACM0` 或 `/dev/can0`；Windows 不需要。

---

## 📄 License

MIT

---

## ☎ 联系

- Issue: https://github.com/vectorBH6/reBotArm_control_py/issues
- Repo: https://github.com/vectorBH6/reBotArm_control_py
