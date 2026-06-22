# Guía de Inicio de Pinocchio y MeshCat para reBot Arm B601-DM

<p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="Licencia: MIT"></a>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Versión Python">
    <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg" alt="Plataforma">
    <img src="https://img.shields.io/badge/Framework-Pinocchio-yellow.svg" alt="Pinocchio">
</p>

<p align="center"><strong>Brazo Robótico 6-DOF · Multi-Motor · Cinemática · Planificación de Trayectoria · Licencia MIT</strong></p>

<p align="center">
    <a href="./README_zh.md">简体中文</a> &nbsp;|&nbsp;
    <a href="./README.md">English</a> &nbsp;|&nbsp;
    <a href="./README_JP.md">日本語</a>&nbsp;|&nbsp;
    <a href="./README_Fr.md">français</a>&nbsp;|&nbsp;
    <a href="./README_es.md">Español</a>
</p>

---

## 📖 Introducción

**reBotArm Control**: Biblioteca Python para brazos robóticos reBot Arm B601 — control de motores, cinemática, planificación de trayectorias.

- 🦾 Modelos duales: B601-DM (Damiao) / B601-RS (RobStride)
- 🧮 Cinemática: FK/IK mediante Pinocchio
- 🛤️ Trayectoria: Geodésica SE(3) + seguimiento CLIK
- 🔧 Configuración: Basada en YAML

---

## ⚙️ Instalación (Linux / Windows)

### 1. Instalar Anaconda / Miniconda
Descarga [Miniconda](https://docs.conda.io/en/latest/miniconda.html). En Windows, abre **Anaconda PowerShell Prompt** (no PowerShell normal).

### 2. Crear entorno e instalar dependencias
```bash
conda create -n robotarm python=3.10 -y
conda activate robotarm
git clone https://github.com/vectorBH6/reBotArm_control_py.git
cd reBotArm_control_py
pip install -e .
pip install motorbridge
```

> No uses el `.venv/` del proyecto. Siempre ejecuta `conda activate robotarm` primero.

### 3. Verificar
```bash
motorbridge-cli scan --vendor robstride --channel can0@1000000 --start-id 1 --end-id 5
```
Deberías ver 5 motores (ajusta la cantidad a tu hardware).

---

## 🪟 Windows: PEAK PCAN-USB

En Windows, `motorbridge` usa PCAN-Basic para comunicarse con adaptadores PCAN-USB.

| Elemento | Qué hacer |
|---|---|
| **Controlador** | Descarga PCAN-Driver desde https://www.peak-system.com/fileadmin/media/files/PEAK-System_Driver-Setup.zip (incluye `PCANBasic.dll` + PCAN-View) |
| **Verificar DLL** | `Test-Path C:\Windows\System32\PCANBasic.dll` → `True` |
| **Nombres de canal** | `can0` / `can1` → `PCAN_USBBUS1` / `PCAN_USBBUS2`; `can0@1000000` = 1 Mbps |
| **Baudrates por defecto** | RS06 = 1 Mbps; RS00 / Damiao = 500 kbps |
| **Editar config** | En `config/rebotarm_rs.yaml`, configura `channel: can0@1000000` (`rate` = Hz del bucle de control, no baudrate CAN) |
| **Codificación YAML** | Windows usa GBK por defecto, lo que rompe archivos YAML con comentarios en chino. `rebotarm.py` ya usa `encoding="utf-8"` — no requiere cambios manuales. |
| **Permisos** | No necesitas `chmod`; permite motorbridge en Defender / 360 si lo solicita |
| **VM / WSL2** | PCAN-USB debe pasarse al host Windows; no usable directamente dentro de VMs |

### Solución de problemas en Windows
| Síntoma | Solución |
|---|---|
| `ModuleNotFoundError: motorbridge` | Entorno Python incorrecto → `conda activate robotarm` |
| `UnicodeDecodeError: 'gbk'` | Ver fila de codificación YAML arriba |
| Scan no responde | Prueba otro baudrate (`@500000` ↔ `@1000000`); verifica con PCAN-View |
| Motor no responde | Verifica resistencias de terminación 120Ω; confirma que `motor_id` coincida con el scan |

---

## 🔌 Configuración de Hardware

| Motor | Plataforma | Transporte | Canal / Puerto | Baudrate |
|---|---|---|---|---|
| Damiao | Linux | Puente serie | `/dev/ttyACM0` | 921600 |
| Damiao | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS00 | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS06 | Linux/Windows | SocketCAN / PCAN | `can0@1000000` | 1 Mbps |

SocketCAN en Linux:
```bash
sudo ip link set can0 up type can bitrate 1000000
```

El puente serie Damiao requiere `--transport dm-serial`. Regla de ID de feedback: `feedback_id = motor_id + 0x10`.

---

## 📁 Estructura del Proyecto

```
reBotArm_control_py/
├── config/                 # Config YAML
├── example/                # Ejemplos (numerados 0x01…9)
├── reBotArm_control_py/    # Núcleo (actuator / kinematics / controllers / trajectory)
└── urdf/                   # Modelo URDF
```

---

## 🎮 Programas de Ejemplo

Siempre ejecuta `conda activate robotarm` primero.

| # | Archivo | Descripción |
|---|---|---|
| 0x01 | `0x01rs06_test.py` / `0x01damiao_test.py` | Consola mono-motor (`ping` / `enable` / `mode mit` / `mit <pos>`) |
| 2 | `2_zero_and_read.py` | Calibración de cero + ángulos en tiempo real |
| 3 | `3_mit_control.py` | Modo MIT (posición + velocidad + torque) |
| 4 | `4_pos_vel_control.py` | Modo POS_VEL |
| 5 | `5_fk_test.py` | FK: 6 ángulos articulares (°) → pose del efector |
| 6 | `6_ik_test.py` | IK: pose del efector → ángulos articulares |
| 7 | `7_arm_ik_control.py` | Control IK en tiempo real (`x y z [r p y]`) |
| 8 | `8_arm_traj_control.py` | Geodésica SE(3) + CLIK (`x y z [r p y] [duration]`) |
| 9 | `9_gravity_compensation.py` | Compensación de gravedad con Pinocchio (`tau = g(q)`, kp=2 kd=1) |

**Permisos**: Control en máquina real en Linux → `sudo chmod 666 /dev/ttyACM0` o `/dev/can0` primero; en Windows → no necesitas chmod.

---

## 📄 Licencia

MIT

---

## ☎ Contacto

- Issues: https://github.com/vectorBH6/reBotArm_control_py/issues
- Repo: https://github.com/vectorBH6/reBotArm_control_py
