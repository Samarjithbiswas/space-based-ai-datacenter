#!/usr/bin/env python3
"""
Report I  --  Passive thermal feasibility of a TPU-class node in low Earth orbit.

Self-contained reproduction of the original (Part I) thermal-feasibility study. Running this file
reproduces every number in that report: the heat-load budget, the radiator temperature by
Newton-Raphson on the Stefan-Boltzmann balance, the junction-to-radiator resistance chain (before and
after optimization), the junction temperature and its margin, the single-heat-pipe-failure case, the
chip-level passive thermal wall, the external (solar, albedo, Earth-infrared) loads, and the eclipse
transient by lumped capacitance.

No third-party dependencies: standard-library `math` only. Run with:  python report_one_thermal.py

Parameter set and sources
-------------------------
Reference node: four accelerators at 300 W each plus avionics and parasitics, on a dawn-dusk
sun-synchronous orbit at 650 km. Radiator: two 2 m^2 panels (4 m^2 planform), treated single-sided,
Z-93 white paint at end-of-life emissivity 0.85. Constants: Stefan-Boltzmann sigma, Earth radius and
infrared/albedo values per the standard space-environment references. The solar constant is taken as
1367 W/m^2 as in the original study (the modern TSIS-1 value is 1361 W/m^2; this choice changes the
solar term by under one percent and does not affect any conclusion).
"""
import math

# ---------------------------------------------------------------- physical constants
SIGMA = 5.670374419e-8      # Stefan-Boltzmann constant [W/m^2/K^4]
R_E = 6371e3               # Earth mean radius [m]
S0 = 1367.0                # solar constant used in Report I [W/m^2] (modern value 1361)
Q_IR = 237.0               # Earth outgoing longwave (infrared) flux [W/m^2]
ALBEDO = 0.30              # Earth Bond albedo [-]
J_LIMIT = 125.0            # accelerator junction-temperature limit [C]

# ---------------------------------------------------------------- node parameters
N_TPU, P_TPU = 4, 300.0    # accelerators and per-chip power [W]
P_AVIONICS = 150.0
P_PARASITIC = 100.0        # lumped external load, radiators edge-on (optimized orientation)
AREA = 4.0                 # radiator planform [m^2] (two 2 m^2 panels), single-sided emitter
EPS = 0.85                 # Z-93 emissivity at end of life
H = 650e3                  # orbit altitude [m]


def heat_load():
    compute = N_TPU * P_TPU
    total = compute + P_AVIONICS + P_PARASITIC
    return compute, total


def radiator_temperature(Q, A, eps=EPS, T0=300.0, tol=1e-2, verbose=False):
    """Radiator temperature [C] from f(T) = Q - eps*sigma*A*T^4 by Newton-Raphson.
    f'(T) = -4*eps*sigma*A*T^3. Deep-space sink dropped (T_cmb^4/T^4 ~ 1e-8)."""
    T = T0
    for k in range(1, 50):
        f = Q - eps * SIGMA * A * T ** 4
        fp = -4 * eps * SIGMA * A * T ** 3
        step = f / fp
        T -= step
        if verbose:
            print(f"      iter {k}: T = {T - 273.15:7.3f} C   (step {abs(step):.4f} K)")
        if abs(step) < tol:
            break
    return T - 273.15


def resistance_chain(r_jc=0.150, r_tim=0.040, r_base=0.060, r_pipe=0.080, r_rad=0.020):
    """Series junction-to-radiator thermal resistance [K/W] and its components."""
    comps = {"junction-to-case": r_jc, "interface (TIM)": r_tim, "cold-plate base": r_base,
             "heat pipe": r_pipe, "radiator": r_rad}
    return sum(comps.values()), comps


def junction_temp(T_rad, P_chip, R_th):
    return T_rad + P_chip * R_th


def view_factor(h=H):
    r = R_E + h
    return 0.5 * (1 - math.sqrt(1 - (R_E / r) ** 2))


def external_loads(alpha_s=0.15, A=AREA, eps=EPS, h=H):
    """Solar, albedo, and Earth-infrared loads [W] on the surface."""
    F = view_factor(h)
    solar = S0 * alpha_s * A                       # full-sun, normal incidence (cos theta = 1)
    albedo = S0 * ALBEDO * F * alpha_s * A
    earth_ir = Q_IR * F * eps * A
    return F, solar, albedo, earth_ir


def eclipse_transient(t_s, T0_C, m=54.0, cp=900.0, A=AREA, eps=EPS, d_solar=-100.0):
    """Lumped-capacitance eclipse response. Returns (T_at_t [C], tau [s], dT_ss [K], h_rad).
    tau = m*cp/(h_rad*A), h_rad = 4*eps*sigma*T0^3, Bi << 0.1 so lumped capacitance holds."""
    T0 = T0_C + 273.15
    h_rad = 4 * eps * SIGMA * T0 ** 3
    tau = m * cp / (h_rad * A)
    dT_ss = d_solar / (h_rad * A)
    T_t = T0 + dT_ss * (1 - math.exp(-t_s / tau))
    return T_t - 273.15, tau, dT_ss, h_rad


def report():
    line = "=" * 74
    print(line); print(" REPORT I  --  PASSIVE THERMAL FEASIBILITY OF A TPU NODE AT 650 km"); print(line)

    compute, Q = heat_load()
    print(f"\n1. Heat load")
    print(f"   compute {N_TPU}x{P_TPU:.0f} W = {compute:.0f} W  +  avionics {P_AVIONICS:.0f} W"
          f"  +  parasitic {P_PARASITIC:.0f} W")
    print(f"   total Q = {Q:.0f} W")

    print(f"\n2. Radiator temperature (Newton-Raphson on Stefan-Boltzmann, A={AREA} m^2, eps={EPS})")
    T_rad = radiator_temperature(Q, AREA, verbose=True)
    print(f"   T_radiator = {T_rad:.2f} C")

    print(f"\n3. Junction-to-radiator resistance chain [K/W]")
    R_before, comps_b = resistance_chain()
    R_after, _ = resistance_chain(r_tim=0.020, r_pipe=0.050)   # liquid-metal TIM + better vapor chamber
    for name, v in comps_b.items():
        print(f"   {name:18s} {v:.3f}")
    print(f"   total before optimization = {R_before:.3f} ;  after optimization = {R_after:.3f}")

    Tj = junction_temp(T_rad, P_TPU, R_after)
    margin = J_LIMIT - Tj
    print(f"\n4. Junction temperature and margin (per chip, R_th = {R_after:.3f} K/W)")
    print(f"   T_j = {T_rad:.2f} + {P_TPU:.0f} x {R_after:.3f} = {Tj:.1f} C")
    print(f"   margin to {J_LIMIT:.0f} C limit = {margin:.1f} C")

    print(f"\n5. Single-heat-pipe failure (8 pipes -> 7)")
    dR_pub = 0.080 * (8 / 7 - 1)                 # published: scale the 0.080 nominal pipe value
    R_fail_pub = R_after + dR_pub
    Tj_fail_pub = junction_temp(T_rad, P_TPU, R_fail_pub)
    dR_alt = 0.050 * (8 / 7 - 1)                 # alternative: scale the optimized 0.050 pipe value
    Tj_fail_alt = junction_temp(T_rad, P_TPU, R_after + dR_alt)
    print(f"   published convention: dR = +{dR_pub:.4f} -> R = {R_fail_pub:.4f} -> T_j = {Tj_fail_pub:.1f} C"
          f"  (margin {J_LIMIT - Tj_fail_pub:.1f} C)")
    print(f"   alternative (scale optimized pipe): dR = +{dR_alt:.4f} -> T_j = {Tj_fail_alt:.1f} C")

    print(f"\n6. Passive thermal wall: max chip power within the {J_LIMIT:.0f} C budget")
    P_max = (J_LIMIT - T_rad) / R_after
    print(f"   P_max = ({J_LIMIT:.0f} - {T_rad:.1f}) / {R_after:.3f} = {P_max:.0f} W per chip")
    print(f"   above this, the interface alone exceeds the budget -> liquid cooling at the die")

    print(f"\n7. External loads (alpha_s = 0.15, A = {AREA} m^2)")
    F, solar, albedo, earth_ir = external_loads()
    print(f"   Earth view factor F = {F:.3f}")
    print(f"   solar    = S0*alpha_s*A           = {solar:.0f} W")
    print(f"   albedo   = S0*a*F*alpha_s*A        = {albedo:.0f} W")
    print(f"   Earth-IR = q_IR*F*eps*A            = {earth_ir:.0f} W")
    print(f"   Earth-facing worst case ~ {albedo + earth_ir:.0f} W; the edge-on baseline lumps to "
          f"{P_PARASITIC:.0f} W")

    print(f"\n8. Eclipse transient (lumped capacitance, dawn-dusk grazing, t = 300 s)")
    T_ec, tau, dT_ss, h_rad = eclipse_transient(300.0, T_rad)
    Tj_ec = junction_temp(T_ec, P_TPU, R_after)
    print(f"   h_rad = 4*eps*sigma*T0^3 = {h_rad:.2f} W/m^2/K ;  tau = {tau:.0f} s (~{tau/60:.0f} min)")
    print(f"   steady drop dT_ss = {dT_ss:.2f} K ;  T_radiator(300 s) = {T_ec:.2f} C ; "
          f"T_j(300 s) = {Tj_ec:.1f} C")
    print(f"   the dawn-dusk orbit barely enters shadow, so the eclipse effect is negligible")

    # ---- self-checks against the published values ----
    print(f"\n{line}\n SELF-CHECKS (published Report I values)\n{line}")
    checks = [
        ("radiator temperature ~ 21.3 C", abs(T_rad - 21.3) < 0.3),
        ("junction temperature ~ 111.3 C", abs(Tj - 111.3) < 0.5),
        ("margin ~ 13.7 C (published ~13.6, rounding)", abs(margin - 13.7) < 0.6),
        ("failed-pipe junction ~ 114.8 C", abs(Tj_fail_pub - 114.8) < 0.5),
        ("passive wall ~ 346 W per chip", abs(P_max - 346) < 5),
        ("view factor ~ 0.290", abs(F - 0.290) < 0.005),
    ]
    ok = True
    for name, passed in checks:
        print(f"   [{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed
    print(line)
    print(" ALL CHECKS PASS" if ok else " SOME CHECKS FAILED")
    print(line)
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if report() else 1)
