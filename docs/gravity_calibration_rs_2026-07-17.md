# RS-build gravity calibration — 2026-07-17

Measured on a RobStride reBot DevArm (rs-06 ×3 + rs-00 ×4, ids 1–7, can0,
48 V) with per-joint PD sweeps: the holding torque is estimated from the MIT
tracking error, `tau ≈ kp·(target − q) − kd·v` (kp assumed exact N·m/rad),
~2800 samples per fit, up+down passes to separate Coulomb friction. Raw data
and harness: `gravity_tune/` in the rig workspace (pd_sweep_id.py,
auto_float_test.py). Validation: single-joint autonomous float — elbow at
q=0.9 rad drifted −0.0002 rad over 12 s with the corrected feedforward.

## Findings relevant to `9_gravity_compensation.py`

1. **`get_positions()` returned frozen values on RS firmware** (type-0x18
   stream frames are not decoded by `get_state()`), so g(q) was evaluated at
   q=0 forever — the compensation pushed a constant g(0) regardless of pose.
   Fixed in this PR: RobStride joints now read `mechPos` (0x7019) live.
2. **Motor zeros sit at the mechanical hard stops, which are NOT the URDF
   zeros.** Measured zero offsets (add to mechPos before g(q), URDF-of-this-
   repo frame): joint2 ≈ +0.28 rad, joint3 ≈ +0.40, joint4 ≈ +0.30 rad
   (joint5 not well resolved). Without these, g(q) is wrong everywhere.
3. **Link masses are fine — stop retuning them.** With the zero offset
   applied, the measured elbow gravity amplitude matches the URDF model
   within ±2% (7.15–7.19 N·m measured vs 7.05 modeled). This holds for both
   this repo's mass set and the Isaacsim-repo (PR#3) mass set.
4. **The cable harness acts as a real torsion spring on the shoulder**:
   ≈ +4.5 N·m/rad in joint2 (with ≈ −2.4 N·m bias), comparable to or larger
   than the gravity term in the folded/extended configurations. A mass-only
   Pinocchio model cannot express it — add an additive per-joint term.
5. **The wrist pitch (joint4) carries ~×1.66 the modeled gravity torque**
   (unmodeled cable/harness weight toward the gripper).
6. **Coulomb friction** ≈ 0.6 (j2), 0.43 (j3), 0.31 (j4), 0.24 (j5) N·m.
7. **mechVel (0x701A) is not rad/s on this firmware** (scale 2.6–4.8 vs
   dq/dt, sign inconsistent). Use finite differences of mechPos.

## Practical feedforward correction (motor frame)

```
tau_ff_j = k_j * g_j(q + off_j) + spring_j(q_j) + C_j     [N·m]

joint2: k=1.34, off=+0.28, spring=+4.51*q2, C=-2.37   (rms 2.4 — cable is
        nonlinear; per-posture LUT fits better, see tables below)
joint3: k=1.00, off=+0.40 (repo URDF frame: -0.40 motor), C=-2.33  (rms 1.2)
joint4: k=1.66, off=+0.30, C=-1.39                                 (rms 0.26)
joint5: k=1.44, off≈-1.08 (poorly resolved), C=+0.19               (rms 0.08)
```

Empirical single-joint tables (motor frame, `A·sin(q+phi)+C`), measured with
the untested joints held at the rest pose:

| joint | A [N·m] | phi [rad] | C [N·m] | window [rad] |
|---|---|---|---|---|
| joint2 (elbow 0.0) | 7.97 | −2.334 | +7.50 | 0 → 2.0 |
| joint2 (elbow 0.8) | 7.77 | +2.867 | +2.35 | 0 → 2.0 |
| joint2 (elbow 1.6) | 11.52 | +1.800 | −3.59 | 0 → 2.0 |
| joint3 | 7.19 | +1.442 | −2.44 | 0 → 2.28 |
| joint4 | 3.25 | +1.442 | −1.35 | 0 → 1.2 |
| joint5 | 0.54 | −2.082 | +0.63 | 0 → 1.2 |

Caveats: torque scale rides on the MIT kp being exact N·m/rad (no independent
torque sensor); joint2 tables mix gravity + cable and are only valid at the
listed elbow posture; sign convention is the motor/mechPos frame, which maps
to this repo's URDF with identity and to the Seeed reBot-Isaacsim URDF with
`q_urdf = −q_motor`.
