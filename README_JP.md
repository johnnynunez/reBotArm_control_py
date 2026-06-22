# reBot Arm B601-DM の Pinocchio と MeshCat 入門ガイド

<p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg" alt="Platform">
    <img src="https://img.shields.io/badge/Framework-Pinocchio-yellow.svg" alt="Pinocchio">
</p>

<p align="center"><strong>6自由度ロボットアーム · マルチモーター · 運動学 · 軌道計画 · MITライセンス</strong></p>

<p align="center">
    <a href="./README_zh.md">简体中文</a> &nbsp;|&nbsp;
    <a href="./README.md">English</a> &nbsp;|&nbsp;
    <a href="./README_JP.md">日本語</a>&nbsp;|&nbsp;
    <a href="./README_Fr.md">français</a>&nbsp;|&nbsp;
    <a href="./README_es.md">Español</a>
</p>

---

## 📖 プロジェクト概要

**reBotArm Control**: reBot Arm B601 シリーズ向け Python 制御ライブラリ — モータ制御、运动学、軌道計画。

- 🦾 デュアルモデル: B601-DM（達妙）/ B601-RS（RobStride）
- 🧮 運動学: Pinocchio による FK/IK
- 🛤️ 軌道: SE(3) 測地線 + CLIK 追従
- 🔧 設定: YAML ベース

---

## ⚙️ インストール（Linux / Windows 共通）

### 1. Anaconda / Miniconda をインストール
[Miniconda](https://docs.conda.io/en/latest/miniconda.html) をダウンロード。Windows ユーザーは **Anaconda PowerShell Prompt** を管理者として開くこと（通常の PowerShell では conda コマンドが認識されない）。

### 2. 環境作成＋依存関係インストール
```bash
conda create -n robotarm python=3.10 -y
conda activate robotarm
git clone https://github.com/vectorBH6/reBotArm_control_py.git
cd reBotArm_control_py
pip install -e .
pip install motorbridge
```

> プロジェクトの `.venv/` は使用禁止。必ず最初に `conda activate robotarm` を実行すること。

### 3. 動作確認
```bash
motorbridge-cli scan --vendor robstride --channel can0@1000000 --start-id 1 --end-id 5
```
5 つのモータが検出されれば OK（ハードウェアの数に合わせて調整）。

---

## 🪟 Windows: PEAK PCAN-USB

Windows では `motorbridge` が PCAN-Basic を使って PCAN-USB アダプタと通信する。

| 項目 | 手順 |
|---|---|
| **ドライバ** | https://www.peak-system.com/quick-drivers から PCAN-Driver をダウンロード（`PCANBasic.dll` + PCAN-View が含まれる） |
| **DLL 確認** | `Test-Path C:\Windows\System32\PCANBasic.dll` → `True` |
| **チャネル命名** | `can0` / `can1` → `PCAN_USBBUS1` / `PCAN_USBBUS2`; `can0@1000000` = 1 Mbps |
| **デフォルトbaudrate** | RS06 = 1 Mbps; RS00 / 達妙 = 500 kbps |
| **設定変更** | `config/rebotarm_rs.yaml` 内の `channel: can0@1000000` を設定（`rate` は制御ループの Hz で、CAN baudrate ではない） |
| **YAML エンコーディング** | Windows 標準は GBK で、中国語コメント付き YAML を開くとエラーになる。`rebotarm.py` はすでに `encoding="utf-8"` を使用—no manual fix needed. |
| **権限** | `chmod` 不要; Defender / 360 が初回ブロックしたら許可 |
| **VM / WSL2** | PCAN-USB は Windows ホストにパススルー必須。VM 内部からは使用不可 |

### Windows トラブルシューティング
| 症状 | 対処 |
|---|---|
| `ModuleNotFoundError: motorbridge` | Python 環境錯誤 → `conda activate robotarm` |
| `UnicodeDecodeError: 'gbk'` | 上記 YAML エンコーディングの項目参照 |
| scan 無応答 | baudrate を変更（`@500000` ↔ `@1000000`）；PCAN-View でフレーム確認 |
| モータ応答なし | 120Ω 終端抵抗確認；`motor_id` と scan 結果の一致確認 |

---

## 🔌 ハードウェア設定

| モータ | プラットフォーム | 通信方式 | チャネル / ポート | Baudrate |
|---|---|---|---|---|
| 達妙 | Linux | シリアルブリッジ | `/dev/ttyACM0` | 921600 |
| 達妙 | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS00 | Linux/Windows | SocketCAN / PCAN | `can0@500000` | 500 kbps |
| RS06 | Linux/Windows | SocketCAN / PCAN | `can0@1000000` | 1 Mbps |

Linux SocketCAN 起動:
```bash
sudo ip link set can0 up type can bitrate 1000000
```

達妙シリアルブリッジは `--transport dm-serial` が必要。フィードバック ID 規則: `feedback_id = motor_id + 0x10`。

---

## 📁 プロジェクト構成

```
reBotArm_control_py/
├── config/                 # YAML 設定ファイル
├── example/                # サンプル（0x01…9）
├── reBotArm_control_py/    # コア (actuator / kinematics / controllers / trajectory)
└── urdf/                   # URDF モデル
```

---

## 🎮 サンプルプログラム

必ず最初に `conda activate robotarm` を実行すること。

| # | ファイル | 説明 |
|---|---|---|
| 0x01 | `0x01rs06_test.py` / `0x01damiao_test.py` | 単一モータコンソール (`ping` / `enable` / `mode mit` / `mit <pos>`) |
| 2 | `2_zero_and_read.py` | ゼロキャリブレーション + リアルタイム角度 |
| 3 | `3_mit_control.py` | MIT モード（位置＋速度＋トルク） |
| 4 | `4_pos_vel_control.py` | POS_VEL モード |
| 5 | `5_fk_test.py` | FK: 6 関節角度（度）→ エンドエフェクタ姿勢 |
| 6 | `6_ik_test.py` | IK: エンドエフェクタ姿勢 → 関節角度 |
| 7 | `7_arm_ik_control.py` | IK リアルタイム制御 (`x y z [r p y]`) |
| 8 | `8_arm_traj_control.py` | SE(3) 測地線 + CLIK (`x y z [r p y] [duration]`) |
| 9 | `9_gravity_compensation.py` | Pinocchio 重力補償 (`tau = g(q)`, kp=2 kd=1) |

**権限**: Linux 実機制御 → 事前に `sudo chmod 666 /dev/ttyACM0` または `/dev/can0`; Windows → chmod 不要。

---

## 📄 ライセンス

MIT

---

## ☎ お問い合わせ

- Issue: https://github.com/vectorBH6/reBotArm_control_py/issues
- Repo: https://github.com/vectorBH6/reBotArm_control_py
