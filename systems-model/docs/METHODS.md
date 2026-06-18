# Methods: governing equations by subsystem

Every model is first-order and derived from first principles; each module docstring carries the
equation and its source. Worked examples are checked in `validate.py`.

| Subsystem | Module | Core equations |
|---|---|---|
| Orbit | `orbit` | `v=√(μ/a)`; `T=2π√(a³/μ)`; SSO from J2 nodal-precession match; `β*=asin(R_E/(R_E+h))`; decay `da/dt=−C_D(A/m)ρ√(μa)` |
| Relative dynamics | `orbit` | Clohessy-Wiltshire: mean motion `n=√(μ/a³)`; secular along-track drift `x≈1.5·a_diff·t²` |
| Thermal | `thermal` | `Q=εσA(T⁴−T_cmb⁴)`; `A=Q/(εσT⁴·n·(1−f_p))`; `T_j=T_rad+Q·R_th`; eclipse `τ=mc_p/(h_rad A)`, `h_rad=4εσT³` |
| Power | `power` | `P=S0·A·η(T,life)·packing·path`; `η(T)=η₀(1+k_T(T−28))`; battery `m=E/(DoD·e_sp)` |
| ADCS | `adcs` | divergence `Θ=2.44λ/D`; pointing loss `exp(−2θ_err²/θ_div²)`; GG torque `1.5n²ΔI·sin2θ` |
| Comms | `comms` | `G=(πD/λ)²`; `L_fs=(4πR/λ)²`; `P_rx=P_tx+2G−L_fs−L_point−L_atm−L_optics`; latency `d/v` |
| Radiation | `radiation`/`environment` | `D(x)=D₀e^(−x/λ)+D_∞`; SEU `R=σ_seu·φ·N_bits`; shielding mass `A·t·ρ` |
| Debris | `debris` | `P=1−e^(−ΦANt)`; cascade `P_hit=1−e^(−N_f r_t²/4d²)` |
| Propulsion | `propulsion` | drag make-up `½ρv²C_D(A/m)·t`; Hohmann `Δv=v_c1(1−√(2r₂/(r₁+r₂)))`; `m_p=m_dry(e^(Δv/I_sp g₀)−1)` |
| Reliability | `reliability` | `R(t)=e^(−t/MTBF)`; k-of-n `Σ C(n,i)pⁱ(1−p)^(n−i)`; capacity `min(1, n·p/n_req)` |
| Compute | `compute` | delivered `=n·peak·MFU·avail`; effective PUE `=(P_tot/P_compute)/avail` |
| Economics | `economics` | `C_sat=p·m+C_hw`; cross-over `p*=C_hw/m`; TCO `=CAPEX+10·OPEX` |
| Integration | `system` | closes power→array→mass→thermal→Δv→reliability→economics into one design |

Full derivations of the eight headline equations (decay, radiator, debris, cascade, dose,
de-orbit Δv, propellant, junction temperature) are in the companion *Mathematical Formulation*
document of the Part II report. The `thermal.report_i_baseline()` function reproduces the
published Part I steady-state and single-heat-pipe-failure results exactly (validated < 0.1 °C).
