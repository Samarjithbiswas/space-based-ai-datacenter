"""
Orbital AI Data-Center Survivability Model
==========================================

A first-order, fully-sourced engineering model for the survivability, reliability,
and launch architecture of space-based AI compute clusters (companion to the
"Space-Based AI Data Centers, Part II" study; reference architecture: Google
Project Suncatcher, arXiv:2511.19468).

Design goals
------------
* ACCURATE  - every constant is traceable to a primary source (see docs/SOURCES.md);
              physics functions are pure and validated in validate.py.
* PORTABLE  - relative paths only; runs on any OS with numpy + matplotlib.
* HONEST    - first-order models meant to size problems and rank risks, with
              uncertainty shown as bands, not hidden behind point values.

Run
---
    python survivability.py        # regenerates all figures into ./figures
    python validate.py             # checks the worked examples (CI-style)

Author: Samarjith Biswas, PhD  ·  License: MIT
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.patches import Rectangle

# --------------------------------------------------------------------------------------
# Physical constants (SI). Sources in docs/SOURCES.md.
# --------------------------------------------------------------------------------------
MU    = 3.986004418e14   # Earth gravitational parameter  [m^3 s^-2]  (IERS)
R_E   = 6.371e6          # Earth mean radius              [m]
SIGMA = 5.670374419e-8   # Stefan-Boltzmann constant      [W m^-2 K^-4] (CODATA)
G0    = 9.80665          # standard gravity               [m s^-2]
S0    = 1361.0           # solar constant at 1 AU         [W m^-2]      (Kopp & Lean 2011)
T_CMB = 2.725            # cosmic-microwave-background sink [K]         (Fixsen 2009)

# --------------------------------------------------------------------------------------
# Atmosphere: NRLMSIS 2.1 anchors at 600/650/700/800 km for three solar-activity levels.
# Lower-altitude entries extend the profile with realistic scale heights (plotting only).
# Units: kg m^-3. The min->max ratio (~100x) is the dominant lifetime uncertainty.
# --------------------------------------------------------------------------------------
_ALT = np.array([450, 500, 550, 600, 650, 700, 800]) * 1e3
_RHO = {
    "min": np.array([1.3e-13, 6.0e-14, 3.5e-14, 2.0e-14, 1.1e-14, 6.8e-15, 3.5e-15]),  # F10.7~65
    "mod": np.array([1.8e-12, 9.0e-13, 4.8e-13, 3.0e-13, 1.6e-13, 8.3e-14, 2.7e-14]),  # F10.7~140
    "max": np.array([6.0e-12, 4.0e-12, 2.9e-12, 2.1e-12, 1.2e-12, 7.1e-13, 2.6e-13]),  # F10.7~250
}

FIGDIR = Path(__file__).resolve().parent / "figures"

# ======================================================================================
#  PURE PHYSICS  (no plotting; each function is independently testable)
# ======================================================================================
def orbital_velocity(alt_km: float) -> float:
    """Circular orbital speed [m/s]. v = sqrt(mu/a)."""
    a = R_E + alt_km * 1e3
    return float(np.sqrt(MU / a))


def orbital_period(alt_km: float) -> float:
    """Circular orbital period [s]. T = 2*pi*sqrt(a^3/mu)  (Kepler's third law)."""
    a = R_E + alt_km * 1e3
    return float(2 * np.pi * np.sqrt(a**3 / MU))


def atmospheric_density(alt_km: float, scenario: str = "mod") -> float:
    """Neutral mass density [kg/m^3] from log-linear interpolation of NRLMSIS anchors."""
    h = np.clip(alt_km * 1e3, _ALT[0], _ALT[-1])
    return float(np.exp(np.interp(h, _ALT, np.log(_RHO[scenario]))))


def orbital_lifetime(alt_km: float, area_to_mass: float,
                     scenario: str = "mod", cd: float = 2.2) -> float:
    """Natural orbital lifetime [years] by integrating circular-orbit drag decay:

        da/dt = -C_D * (A/m) * rho(h) * sqrt(mu*a)

    derived from the orbital-energy balance dE/dt = -a_drag*v with E = -mu/(2a).
    Integrated with adaptive forward Euler to re-entry at 120 km.
    """
    a = R_E + alt_km * 1e3
    t = 0.0
    year = 3.15576e7
    dt = 3600 * 6
    while a > R_E + 120e3 and t < 2000 * year:
        h = (a - R_E) / 1e3
        a += -cd * area_to_mass * atmospheric_density(h, scenario) * np.sqrt(MU * a) * dt
        t += dt
        dt = 3600 * 48 if (a - R_E) > 500e3 else (3600 * 12 if (a - R_E) > 300e3 else 3600 * 2)
    return t / year


def radiator_area(heat_W: float, temp_C: float, emissivity: float = 0.90,
                  sides: int = 2, parasitic: float = 0.12) -> float:
    """Required radiator area [m^2] from the Stefan-Boltzmann balance:

        A = Q / (eps * sigma * T^4 * n_sides * (1 - parasitic))

    Linear in Q -> there is no economy of scale in radiative cooling.
    """
    T = temp_C + 273.15
    return heat_W / (emissivity * SIGMA * T**4 * sides * (1 - parasitic))


def junction_delta_T(chip_W: float, r_th: float = 0.30) -> float:
    """Junction-to-radiator temperature rise [K] across a series thermal chain, dT = P*R_th.
    Above ~417 W at R_th=0.30 K/W this exceeds the 125 C budget -> active cooling required."""
    return chip_W * r_th


def collision_probability(flux_per_m2_yr: float, cross_section_m2: float,
                          n_sats: int, years: float) -> float:
    """Probability of >=1 catastrophic impact in the cluster (Poisson):

        P = 1 - exp(-Phi * A * N * t)
    """
    return float(1 - np.exp(-flux_per_m2_yr * cross_section_m2 * n_sats * years))


def cascade_neighbor_probability(spacing_m: float, n_fragments: int = 2000,
                                 target_radius_m: float = 2.0) -> float:
    """Probability a given neighbor is struck by >=1 lethal fragment (expanding-shell model):

        P_hit = 1 - exp(-N_f * r_t^2 / (4 * d^2))
    """
    return float(1 - np.exp(-n_fragments * target_radius_m**2 / (4 * spacing_m**2)))


def tid_dose_rate(al_mm: float, band: str = "mid") -> float:
    """Annual total ionizing dose [rad(Si)/yr] behind Al shielding (SHIELDOSE-2/AE8-AP8 class),

        D(x) = D0 * exp(-x/lambda) + D_inf

    calibrated to a ~100-160 rad/yr proton floor (SIRI-1 600 km SSO; Suncatcher proton test).
    """
    lam = 1.7
    lo = 2.0e4 * np.exp(-al_mm / lam) + 100.0
    hi = 3.8e4 * np.exp(-al_mm / lam) + 160.0
    return {"lo": lo, "hi": hi, "mid": 0.5 * (lo + hi)}[band]


def deorbit_delta_v(alt_km: float, perigee_km: float = 180.0) -> float:
    """Delta-v [m/s] for a single retrograde burn lowering perigee (Hohmann), from vis-viva:

        dv = v_c1 * (1 - sqrt(2*r2 / (r1 + r2)))
    """
    r1 = R_E + alt_km * 1e3
    r2 = R_E + perigee_km * 1e3
    v1 = np.sqrt(MU / r1)
    return float(v1 * (1 - np.sqrt(2 * r2 / (r1 + r2))))


def drag_delta_v(alt_km: float, area_to_mass: float, years: float = 5.0,
                 cd: float = 2.2, scenario: str = "mod") -> float:
    """Delta-v [m/s] to make up drag over the mission, integral of a_drag dt."""
    v = orbital_velocity(alt_km)
    a_drag = 0.5 * atmospheric_density(alt_km, scenario) * v**2 * cd * area_to_mass
    return float(a_drag * years * 3.15576e7)


def propellant_mass(delta_v: float, isp_s: float, dry_mass_kg: float = 220.0) -> float:
    """Propellant mass [kg] from the rocket equation, m_p = m_dry*(exp(dv/(Isp*g0)) - 1)."""
    return float(dry_mass_kg * (np.exp(delta_v / (isp_s * G0)) - 1))


def eclipse_critical_beta(alt_km: float) -> float:
    """Critical beta angle [deg] below which eclipses occur, beta* = asin(R_E/(R_E+h))."""
    return float(np.degrees(np.arcsin(R_E / (R_E + alt_km * 1e3))))


# ======================================================================================
#  FIGURE GENERATION
# ======================================================================================
NAVY, ACCENT, COOL = "#16243a", "#c75c2e", "#2f6f8f"
GOOD, WARN, BAD = "#2e7d4f", "#caa12a", "#a3303a"


def _style():
    import matplotlib as mpl
    mpl.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9.5,
        "axes.titlesize": 11.5, "axes.titleweight": "bold", "axes.labelsize": 10,
        "axes.edgecolor": "#33414f", "axes.linewidth": 1.0,
        "axes.grid": True, "grid.color": "#e6e9ec", "grid.linewidth": 0.8,
        "figure.dpi": 135, "savefig.dpi": 175, "savefig.bbox": "tight", "legend.frameon": False,
    })


def _credit(fig, text):
    fig.text(0.005, -0.02, "DATA SOURCE  " + text, ha="left", va="top",
             fontsize=6.7, color="#7a8590", style="italic")


def _tab(fig, label):
    fig.text(0.005, 1.005, label, ha="left", va="bottom", fontsize=10.5, fontweight="bold",
             color="white", bbox=dict(boxstyle="round,pad=0.32", fc=NAVY, ec="none"))


def figure_decay(bus_area_to_mass=3.5 / 233):
    alts = np.linspace(450, 800, 24)
    fig, ax = plt.subplots(figsize=(8.6, 5.3))
    dmin = [orbital_lifetime(h, bus_area_to_mass, "min") for h in alts]
    dmod = [orbital_lifetime(h, bus_area_to_mass, "mod") for h in alts]
    dmax = [orbital_lifetime(h, bus_area_to_mass, "max") for h in alts]
    ax.fill_between(alts, dmax, dmin, color=COOL, alpha=0.16, label="solar-cycle range (min<->max)")
    ax.semilogy(alts, dmod, color=COOL, lw=2.6, label="moderate solar activity (F10.7~140)")
    ax.axhline(5, color=BAD, ls="--", lw=1.5)
    ax.text(452, 5.5, "FCC 5-yr rule (since 2022, effective 2024)", color=BAD, fontsize=8.3)
    ax.axhline(25, color="#555", ls=":", lw=1.2)
    ax.text(452, 27, "25-yr international baseline", color="#555", fontsize=8.3)
    ax.axvline(650, color="#999", ls=":", lw=1.1)
    ax.text(655, 2.2e3, "Suncatcher\n650 km", fontsize=8.5, color="#555")
    ax.set_xlabel("Initial circular altitude (km)")
    ax.set_ylabel("Natural orbital lifetime (years, log)")
    ax.set_title("Natural decay fails the 5-year disposal rule at 650 km  ->  active de-orbit is mandatory")
    ax.set_ylim(0.7, 5e3); ax.legend(loc="upper left", fontsize=8.5)
    _tab(fig, "FIG. 1")
    _credit(fig, "Density: NRLMSIS 2.1 (Picone et al. 2002). Rule: FCC 22-74 (2022). Drag: circular-orbit, C_D=2.2.")
    fig.savefig(FIGDIR / "fig1_orbital_decay.png"); plt.close(fig)


def figure_thermal_wall():
    Q = np.logspace(np.log10(300), np.log10(2e6), 250)
    fig = plt.figure(figsize=(10.0, 5.2))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.18, 1], wspace=0.36)
    axA = fig.add_subplot(gs[0])
    for T_C, c in [(20, COOL), (40, WARN), (60, ACCENT)]:
        axA.loglog(Q / 1e3, radiator_area(Q, T_C), lw=2.5, color=c, label=f"radiator @ {T_C} C")

    def mark(qkW, T, name, dx, dy, c):
        A = radiator_area(qkW * 1e3, T)
        axA.scatter([qkW], [A], s=52, color=c, ec="white", lw=1.1, zorder=5)
        axA.annotate(f"{name}\n{A:,.0f} m^2", (qkW, A), xytext=(qkW * dx, A * dy), fontsize=7.8, color=c)
    mark(0.85, 20, "Starcloud-1\n1x H100, 0.85 kW", 1.25, 0.30, COOL)
    mark(1.45, 20, "Report I\n4 TPU, 1.45 kW", 0.22, 1.7, GOOD)
    mark(120, 40, "GB200 NVL72\nrack, 120 kW", 0.16, 0.40, ACCENT)
    mark(1000, 40, "1 MW node", 0.18, 0.40, BAD)
    axA.scatter([1000], [1200], marker="*", s=170, color="k", zorder=6)
    axA.annotate("Industry rule\n~1,200 m^2/MW", (1000, 1200), xytext=(150, 2100), fontsize=7.8, color="k")
    axA.set_xlabel("Compute heat load (kW, log)"); axA.set_ylabel("Required radiator area (m^2, log)")
    axA.set_title("(a) Cooling scales linearly with power"); axA.legend(loc="upper left", fontsize=8)

    axB = fig.add_subplot(gs[1])
    chips = [("TPU v6e\n~200 W*", 200, COOL), ("TPU\n300 W", 300, "#7fa8bd"),
             ("H100\n700 W", 700, WARN), ("B200\n1000 W", 1000, ACCENT), ("GB200\n1200 W", 1200, BAD)]
    xs = np.arange(len(chips)); dT = [junction_delta_T(p) for _, p, _ in chips]
    axB.bar(xs, dT, color=[c for *_, c in chips], width=0.66)
    axB.axhline(125, color=BAD, ls="--", lw=1.4)
    axB.text(0.1, 128, "125 C junction limit (entire budget)", color=BAD, fontsize=7.8)
    for x, v in zip(xs, dT): axB.text(x, v + 4, f"{v:.0f}", ha="center", fontsize=8)
    axB.set_xticks(xs); axB.set_xticklabels([c[0] for c in chips], fontsize=7.6)
    axB.set_ylabel("Junction->radiator dT at R_th=0.30 K/W (C)")
    axB.set_title("(b) Passive chain saturates >400 W"); axB.set_ylim(0, 400)
    axB.text(0.5, -0.30, "Above the H100, P*R_th alone exceeds the whole 125 C budget ->\n"
             "chip-level liquid/loop-heat-pipe cooling becomes mandatory.",
             transform=axB.transAxes, ha="center", fontsize=7.6, color="#444")
    _tab(fig, "FIG. 2")
    _credit(fig, "Stefan-Boltzmann (eps=0.90, double-sided, 12% parasitic). TDPs: NVIDIA datasheets; *TPU v6e est. (The Next Platform).")
    fig.savefig(FIGDIR / "fig2_thermal_wall.png"); plt.close(fig)


def figure_debris(n_sats=81, cross_section=15.0):
    flo, fmid, fhi = 1e-5, 3e-5, 1e-4
    yrs = np.linspace(0, 10, 200)
    fig = plt.figure(figsize=(9.0, 5.0))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.4, 1], wspace=0.30)
    axA = fig.add_subplot(gs[0])
    P = lambda f, t: collision_probability(f, cross_section, n_sats, t) * 100
    axA.fill_between(yrs, [P(flo, t) for t in yrs], [P(fhi, t) for t in yrs],
                     color=ACCENT, alpha=0.16, label="ORDEM/MASTER range (1e-5 to 1e-4)")
    axA.plot(yrs, [P(fmid, t) for t in yrs], color=ACCENT, lw=2.6, label="central (3e-5 /m^2/yr)")
    axA.axvline(5, color="#999", ls=":", lw=1.1); axA.text(5.07, 3, "5-yr design life", fontsize=8.3, color="#555")
    axA.set_xlabel("Mission elapsed time (years)")
    axA.set_ylabel(f"P(>=1 catastrophic >1 cm hit in {n_sats}-sat cluster) [%]")
    axA.set_title("(a) Catastrophic debris risk, full cluster"); axA.legend(loc="upper left", fontsize=8)
    axB = fig.add_subplot(gs[1])
    spacing = np.array([100, 150, 200, 300, 500, 1000])
    axB.plot(spacing, [cascade_neighbor_probability(d) * 100 for d in spacing], "o-", color=BAD, lw=2.2)
    axB.axvspan(100, 200, color=BAD, alpha=0.09)
    axB.text(150, cascade_neighbor_probability(150) * 100 + 1.4, "Suncatcher\n100-200 m", ha="center", fontsize=7.8, color=BAD)
    axB.set_xlabel("Formation spacing (m)"); axB.set_ylabel("P(a given neighbor struck) [%]")
    axB.set_title("(b) In-cluster cascade coupling")
    _tab(fig, "FIG. 3")
    _credit(fig, "Flux: NASA ORDEM 3.1 / ESA MASTER-8 (Horstmann et al. NTRS 20210011563), 800 km SSO. Population: ESA SER 2025.")
    fig.savefig(FIGDIR / "fig3_debris_risk.png"); plt.close(fig)


def figure_radiation():
    al = np.linspace(1, 20, 90)
    fig = plt.figure(figsize=(9.2, 5.0))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1], wspace=0.30)
    ax1 = fig.add_subplot(gs[0])
    lo = np.array([tid_dose_rate(x, "lo") for x in al]) * 5
    hi = np.array([tid_dose_rate(x, "hi") for x in al]) * 5
    ax1.fill_between(al, lo, hi, color=COOL, alpha=0.16, label="5-yr cumulative (model band)")
    ax1.semilogy(al, (lo + hi) / 2, color=COOL, lw=2.4)
    ax1.axhline(2000, color=BAD, ls="--", lw=1.4); ax1.text(8.5, 2240, "HBM tolerance ~2 krad(Si)", color=BAD, fontsize=8)
    ax1.axhline(750, color=GOOD, ls=":", lw=1.3); ax1.text(8.5, 790, "Google 5-yr requirement 750 rad(Si)", color=GOOD, fontsize=7.8)
    ax1.axvline(10, color="#999", ls=":", lw=1)
    ax1.set_xlabel("Aluminium shielding thickness (mm)"); ax1.set_ylabel("Cumulative 5-yr TID [rad(Si), log]")
    ax1.set_title("(a) Dose vs shielding - 10 mm Al closes it"); ax1.legend(loc="upper right", fontsize=8)
    ax2 = fig.add_subplot(gs[1])
    prot = ["None\n(COTS)", "ECC +\ncheckpoint", "ECC + sel.\nTMR", "Full TMR /\nrad-hard"]
    eff = np.array([0.55, 0.86, 0.78, 0.50]); risk = np.array([0.40, 0.06, 0.02, 0.005])
    x = np.arange(len(prot))
    ax2.bar(x - 0.19, eff * 100, 0.38, color=COOL, label="usable compute %")
    ax2.bar(x + 0.19, risk * 100, 0.38, color=BAD, label="uncorrected-error risk %")
    ax2.set_xticks(x); ax2.set_xticklabels(prot, fontsize=7.8); ax2.set_ylabel("Percent")
    ax2.set_title("(b) Reliability/throughput trade"); ax2.legend(fontsize=7.8, loc="upper right")
    ax2.text(0.5, -0.32, "AI inference tolerates bit-flips better than HPC; ECC+checkpoint is the sweet spot.",
             transform=ax2.transAxes, ha="center", fontsize=7.6, color="#444")
    _tab(fig, "FIG. 4")
    _credit(fig, "TID: SHIELDOSE-2 / AE8-AP8 class, calibrated to SIRI-1 (600 km SSO) & Suncatcher (arXiv:2511.19468). (b) engineering estimate.")
    fig.savefig(FIGDIR / "fig4_radiation.png"); plt.close(fig)


def figure_deltav(bus_area_to_mass=3.5 / 233, dry_mass=220.0):
    dv_d = drag_delta_v(650, bus_area_to_mass)
    dv_f, dv_c = 8.0, 20 * 5 * 0.05
    dv_o = deorbit_delta_v(650)
    dv_m = 0.20 * (dv_d + dv_f + dv_c + dv_o)
    labels = ["Drag\nmake-up", "Formation\nkeeping", "Collision\navoidance", "Controlled\nde-orbit", "Margin\n20%"]
    vals = [dv_d, dv_f, dv_c, dv_o, dv_m]; dvT = sum(vals)
    fig = plt.figure(figsize=(9.4, 4.8))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.3, 1], wspace=0.34)
    axL = fig.add_subplot(gs[0]); xb = np.arange(len(labels))
    axL.bar(xb, vals, color=[COOL, "#7fa8bd", WARN, BAD, "#cccccc"], width=0.7)
    for x, v in zip(xb, vals): axL.text(x, v + 1.5, f"{v:.0f}", ha="center", fontsize=8.3)
    axL.set_xticks(xb); axL.set_xticklabels(labels, fontsize=8); axL.set_ylabel("Delta-v (m/s)"); axL.set_ylim(0, 170)
    axL.set_title(f"(a) Per-satellite delta-v budget (~{dvT:.0f} m/s, 5 yr)")
    axL.text(0.03, 0.96, "Controlled de-orbit dominates -\nthe 'permanent vs disposable' penalty",
             transform=axL.transAxes, ha="left", va="top", fontsize=8, color=BAD,
             bbox=dict(boxstyle="round,pad=0.4", fc="#fdecec", ec=BAD))
    axR = fig.add_subplot(gs[1])
    systems = [("Cold gas\nIsp 70 s", 70, "#9aa7b1"), ("Hydrazine\nIsp 220 s", 220, COOL), ("Electric\nIsp 1500 s", 1500, GOOD)]
    xs = np.arange(len(systems)); pm = [propellant_mass(dvT, isp, dry_mass) for _, isp, _ in systems]
    axR.bar(xs, pm, color=[c for *_, c in systems], width=0.62)
    axR.set_xticks(xs); axR.set_xticklabels([s for s, _, _ in systems], fontsize=8); axR.set_ylabel("Propellant mass (kg)")
    axR.set_title("(b) Propellant for total delta-v\n(375 kg dry bus)")
    for i, v in enumerate(pm): axR.text(i, v + 0.5, f"{v:.0f} kg", ha="center", fontsize=8.3)
    _tab(fig, "FIG. 5")
    _credit(fig, "Drag: NRLMSIS 2.1 @650 km. De-orbit: Hohmann to 180 km. Avoidance: Starlink FCC filing (144,404 / 6 mo). Rocket eqn.")
    fig.savefig(FIGDIR / "fig5_deltav.png"); plt.close(fig)


def figure_launch_cost(launch_mass=233.0, hardware_usd=1.1e6):
    price = np.array([3770, 1500, 600, 300, 200, 100, 30])
    fig = plt.figure(figsize=(9.4, 4.9))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.1, 1], wspace=0.32)
    axA = fig.add_subplot(gs[0])
    axA.plot(price, price * launch_mass / 1e6, "o-", color=ACCENT, lw=2.3, label="launch cost / sat")
    axA.plot(price, (hardware_usd + price * launch_mass) / 1e6, "s--", color=NAVY, lw=2.0, label="all-in / sat")
    axA.set_xscale("log"); axA.invert_xaxis()
    axA.axvspan(3770, 3000, color="#ccc", alpha=0.25); axA.text(3770, 1.3, "Falcon 9\ntoday", fontsize=7.6, color="#555", ha="center")
    axA.axvspan(600, 30, color=GOOD, alpha=0.08); axA.text(120, 2.0, "Starship\ntarget band", fontsize=7.6, color=GOOD, ha="center")
    axA.set_xlabel("Launch price (USD/kg, log -> cheaper)"); axA.set_ylabel("Cost per satellite (USD millions)")
    axA.set_title("(a) Below ~600 USD/kg, hardware dominates"); axA.legend(fontsize=8)
    axB = fig.add_subplot(gs[1])
    era = ["Shuttle\n(prog avg)", "Falcon 9\n(reusable)", "Starship\n(realistic)", "Starship\n(aspirational)"]
    val = [54500, 3770, 300, 30]
    axB.bar(np.arange(len(era)), val, color=[BAD, WARN, COOL, GOOD], width=0.62)
    axB.set_yscale("log"); axB.set_ylabel("USD/kg to LEO (log)")
    for i, v in enumerate(val): axB.text(i, v * 1.15, f"${v:,}", ha="center", fontsize=8)
    axB.set_title("(b) Launch cost trajectory")
    axB.set_xticks(np.arange(len(era))); axB.set_xticklabels(era, fontsize=7.6)
    _tab(fig, "FIG. 6")
    _credit(fig, "Falcon 9: SpaceX list / reusable payload. Starship: target band (analyst + aspirational). Shuttle: program-averaged.")
    fig.savefig(FIGDIR / "fig6_launch_cost.png"); plt.close(fig)


def figure_risk_matrix():
    fig, ax = plt.subplots(figsize=(8.8, 6.0))
    for i in range(5):
        for j in range(5):
            score = (i + 1) * (j + 1)
            c = GOOD if score <= 4 else (WARN if score <= 9 else (ACCENT if score <= 14 else BAD))
            ax.add_patch(Rectangle((i, j), 1, 1, fc=c, ec="white", lw=2, alpha=0.30))
    items = [(0.5, 1.0, "Thermal:\nsingle node", GOOD), (2.0, 2.4, "Thermal:\nMW-scale", WARN),
             (0.8, 2.2, "Radiation\nTID", GOOD), (3.4, 1.6, "Radiation\nSEU tax", WARN),
             (2.3, 4.2, "Debris:\ncascade", BAD), (2.0, 3.6, "Debris:\ncatastrophic", BAD),
             (2.5, 3.0, "Formation\ncontrol", ACCENT), (3.6, 2.2, "End-of-life\nde-orbit", ACCENT),
             (3.6, 3.7, "Economics", BAD)]
    for lk, cq, lab, c in items:
        ax.scatter([lk], [cq], s=120, color=c, ec="white", lw=1.5, zorder=5)
        ax.annotate(lab, (lk, cq), xytext=(lk + 0.10, cq + 0.10), fontsize=7.8, color=NAVY, fontweight="bold")
    ax.set_xlim(0, 5); ax.set_ylim(0, 5)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5]); ax.set_xticklabels(["Very low", "Low", "Moderate", "High", "Very high"], fontsize=8)
    ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5]); ax.set_yticklabels(["Negligible", "Minor", "Moderate", "Major", "Catastrophic"], fontsize=8)
    ax.set_xlabel("LIKELIHOOD ->", fontweight="bold"); ax.set_ylabel("CONSEQUENCE ->", fontweight="bold")
    ax.set_title("Where the real risk lives: cooling is solved; debris, disposal & economics are not", fontsize=11)
    ax.grid(False)
    _tab(fig, "FIG. 7")
    _credit(fig, "Synthesis of Figs. 1-6 and Project Suncatcher (arXiv:2511.19468). Placement is the author's engineering judgement.")
    fig.savefig(FIGDIR / "fig7_risk_matrix.png"); plt.close(fig)


def main():
    FIGDIR.mkdir(exist_ok=True)
    _style()
    figure_decay(); figure_thermal_wall(); figure_debris()
    figure_radiation(); figure_deltav(); figure_launch_cost(); figure_risk_matrix()

    am = 3.5 / 233
    print("=" * 70)
    print(" ORBITAL AI DATA-CENTER SURVIVABILITY  -  HEADLINE NUMBERS")
    print("=" * 70)
    print(f"  Orbital period @650 km        : {orbital_period(650)/60:6.2f} min")
    print(f"  Natural lifetime @650 km (mod): {orbital_lifetime(650, am, 'mod'):6.1f} yr  (FCC rule = 5 yr)")
    print(f"  Radiator area for 1 MW @20 C  : {radiator_area(1e6, 20):6.0f} m^2")
    print(f"  Catastrophic debris P (5 yr)  : {collision_probability(3e-5,15,81,5)*100:6.1f} %")
    print(f"  Neighbor-hit P @150 m spacing : {cascade_neighbor_probability(150)*100:6.1f} %")
    print(f"  5-yr TID behind 10 mm Al      : {tid_dose_rate(10)*5:6.0f} rad(Si)  (HBM limit ~2000)")
    print(f"  De-orbit delta-v @650 km      : {deorbit_delta_v(650):6.1f} m/s")
    print(f"  Propellant (electric, Isp1500): {propellant_mass(189.5,1500):6.1f} kg")
    print("=" * 70)
    print(f"  Figures written to: {FIGDIR}")


if __name__ == "__main__":
    main()
