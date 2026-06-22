# Guide de Démarrage Pinocchio & MeshCat pour reBot Arm B601-DM

<p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Version Python">
    <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg" alt="Plateforme">
    <img src="https://img.shields.io/badge/Framework-Pinocchio-yellow.svg" alt="Pinocchio">
</p>

<p align="center"><strong>Bras Robotique 6-DOF · Multi-Moteur · Cinématique · Planification de Trajectoire · Licence MIT</strong></p>

<p align="center">
    <a href="./README_zh.md">简体中文</a> &nbsp;|&nbsp;
    <a href="./README.md">English</a> &nbsp;|&nbsp;
    <a href="./README_JP.md">日本語</a>&nbsp;|&nbsp;
    <a href="./README_Fr.md">français</a>&nbsp;|&nbsp;
    <a href="./README_es.md">Español</a>
</p>

---

## 📖 Introduction

**reBotArm Control**: Bibliothèque Python pour bras robotiques reBot Arm B601 — contrôle moteur, cinématique, planification de trajectoire.

- 🦾 Modèles doubles : B601-DM (Damiao) / B601-RS (RobStride)
- 🧮 Cinématique : FK/IK via Pinocchio
- 🛤️ Trajectoire : Géodésique SE(3) + suivi CLIK
- 🔧 Configuration : pilotée par YAML

---

## ⚙️ Installation (Linux / Windows)

### 1. Installer Anaconda / Miniconda
Téléchargez [Miniconda](https://docs.conda.io/en/latest/miniconda.html). Sous Windows, ouvrez **Anaconda PowerShell Prompt** (pas PowerShell normal).

### 2. Créer l'environnement et installer les dépendances
```bash
conda create -n robotarm python=3.10 -y
conda activate robotarm
git clone https://github.com/vectorBH6/reBotArm_control_py.git
cd reBotArm_control_py
pip install -e .
pip install motorbridge
```

> Ne pas utiliser le `.venv/` du projet. Toujours exécuter `conda activate robotarm` en premier.

### 3. Vérifier
```bash
motorbridge-cli scan --vendor robstride --channel can0@1000000 --start-id 1 --end-id 5
```
Vous devriez voir 5 moteurs (ajustez le nombre à votre matériel).

---

## 🪟 Windows : PEAK PCAN-USB

Sous Windows, `motorbridge` utilise PCAN-Basic pour communiquer avec les adaptateurs PCAN-USB.

| Élément | Action |
|---|---|
| **Pilote** | Téléchargez PCAN-Driver depuis https://www.peak-system.com/quick-drivers (inclut `PCANBasic.dll` + PCAN-View) |
| **Vérifier DLL** | `Test-Path C:\Windows\System32\PCANBasic.dll` → `True` |
| **Nommage des canaux** | `can0` / `can1` → `PCAN_USBBUS1` / `PCAN_USBBUS2`; `can0@1000000` = 1 Mbps |
| **Baudrates par défaut** | RS06 = 1 Mbps ; RS00 / Damiao = 500 kbps |
| **Éditer config** | Dans `config/rebotarm_rs.yaml`, réglez `channel: can0@1000000` (`rate` = Hz de la boucle de contrôle, pas le baudrate CAN) |
| **Encodage YAML** | Windows utilise GBK par défaut, ce qui casse les fichiers YAML avec des commentaires chinois. `rebotarm.py` utilise déjà `encoding="utf-8"` — aucun correctif manuel nécessaire. |
| **Permissions** | Pas de `chmod` nécessaire ; autorisez motorbridge dans Defender / 360 si demandé |
| **VM / WSL2** | PCAN-USB doit être redirigé vers l'hôte Windows ; non utilisable directement dans les VMs |

### Dépannage Windows
| Symptôme | Solution |
|---|---|
| `ModuleNotFoundError: motorbridge` | Mauvais environnement Python → `conda activate robotarm` |
| `UnicodeDecodeError: 'gbk'` | Voir la ligne encodage YAML ci-dessus |
| Scan ne répond pas | Essayez un autre baudrate (`@500000` ↔ `@1000000`) ; vérifiez avec PCAN-View |
| Moteur ne répond pas | Vérifiez les résistances de terminaison 120Ω ; confirmez que `motor_id` correspond au scan |

---

## 🔌 Configuration Matérielle

| Moteur | Plateforme | Transport | Canal / Port | Baudrate |
|---|---|---|---|---|
| Damiao | Linux | Pont série | `/dev/ttyACM0` | 921600 |
| Damiao | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS00 | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS06 | Linux/Windows | SocketCAN / PCAN | `can0@1000000` | 1 Mbps |

SocketCAN sous Linux :
```bash
sudo ip link set can0 up type can bitrate 1000000
```

Le pont série Damiao nécessite `--transport dm-serial`. Règle d'ID de feedback : `feedback_id = motor_id + 0x10`.

---

## 📁 Structure du Projet

```
reBotArm_control_py/
├── config/                 # Config YAML
├── example/                # Exemples (numérotés 0x01…9)
├── reBotArm_control_py/   # Noyau (actuator / kinematics / controllers / trajectory)
└── urdf/                   # Modèle URDF
```

---

## 🎮 Programmes d'Exemple

Lancez toujours `conda activate robotarm` d'abord.

| # | Fichier | Description |
|---|---|---|
| 0x01 | `0x01rs06_test.py` / `0x01damiao_test.py` | Console mono-moteur (`ping` / `enable` / `mode mit` / `mit <pos>`) |
| 2 | `2_zero_and_read.py` | Calibration du zéro + angles en temps réel |
| 3 | `3_mit_control.py` | Mode MIT (position + vitesse + couple) |
| 4 | `4_pos_vel_control.py` | Mode POS_VEL |
| 5 | `5_fk_test.py` | FK : 6 angles articulaires (°) → pose de l'effecteur |
| 6 | `6_ik_test.py` | IK : pose de l'effecteur → angles articulaires |
| 7 | `7_arm_ik_control.py` | Contrôle IK en temps réel (`x y z [r p y]`) |
| 8 | `8_arm_traj_control.py` | Géodésique SE(3) + CLIK (`x y z [r p y] [duration]`) |
| 9 | `9_gravity_compensation.py` | Compensation de gravité via Pinocchio (`tau = g(q)`, kp=2 kd=1) |

**Permissions** : Contrôle sur machine réelle sous Linux → `sudo chmod 666 /dev/ttyACM0` ou `/dev/can0` d'abord ; sous Windows → pas de chmod nécessaire.

---

## 📄 Licence

MIT

---

## ☎ Contact

- Issues : https://github.com/vectorBH6/reBotArm_control_py/issues
- Dépôt : https://github.com/vectorBH6/reBotArm_control_py
