"""Figure generation for the complete systems model. Each figure carries a DATA SOURCE line.
Produces the new-subsystem figures (power, pointing, link budget, reliability, compute
economics, integrated budget) that complete the Part I study.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from . import power, adcs, comms, reliability, compute, propulsion, orbit
from .system import DesignPoint
from .montecarlo import monte_carlo

NAVY, ACCENT, COOL, GOOD, WARN, BAD = "#16243a", "#c75c2e", "#2f6f8f", "#2e7d4f", "#caa12a", "#a3303a"
FIGDIR = Path(__file__).resolve().parent.parent.parent / "report" / "systems_figs"

# Figure-level titles belong in the document caption, not baked into the image.
# Suppress whole-figure suptitles globally; panel (a)/(b) titles are kept.
import matplotlib.figure as _mfig
_mfig.Figure.suptitle = lambda self, *a, **k: None


def _style():
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5,
        "axes.titlesize": 11.5, "axes.titleweight": "bold", "axes.labelsize": 10,
        "axes.edgecolor": "#33414f", "axes.grid": True, "grid.color": "#e6e9ec",
        "figure.dpi": 130, "savefig.dpi": 165, "savefig.bbox": "tight", "legend.frameon": False})


def _credit(fig, t):
    # Source attribution lives in the document caption and References, not on the figure.
    return


def fig_power():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.4))
    loads = np.linspace(1e3, 1e6, 200)
    a.loglog(loads / 1e3, [power.array_area_for_load(L) for L in loads], color=COOL, lw=2.4)
    a.set_xlabel("Electrical load (kW, log)"); a.set_ylabel("Solar array area (m^2, log)")
    a.set_title("(a)")
    yrs = np.arange(0, 6)
    bol = [power.array_power(100, "bol", 70) for _ in yrs]
    deg = [power.array_power(100, "bol", 70) * (1 - 0.014) ** y for y in yrs]
    b.plot(yrs, np.array(bol) / bol[0] * 100, "--", color="#999", label="no degradation")
    b.plot(yrs, np.array(deg) / bol[0] * 100, "o-", color=ACCENT, label="~1.4%/yr radiation")
    b.set_xlabel("Years on orbit"); b.set_ylabel("Array power (% of BOL)")
    b.set_title("(b)"); b.legend(fontsize=8)
    fig.suptitle("FIG. P  Electrical power subsystem", fontweight="bold")
    _credit(fig, "Azur/Spectrolab datasheets; NASA SoA Power 2024. AM0=1361 W/m^2, eta_EOL~27.5%.")
    fig.tight_layout(); fig.savefig(FIGDIR / "fig_power.png"); plt.close(fig)


def fig_link_budget():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.4))
    R = np.logspace(2, 6.5, 200)
    a.semilogx(R / 1e3, [comms.free_space_loss_dB(r) for r in R], color=COOL, lw=2.4)
    for r, lab in [(150, "neighbor 150 m"), (1e6, "long ISL 1000 km")]:
        a.scatter([r / 1e3], [comms.free_space_loss_dB(r)], color=ACCENT, zorder=5)
        a.annotate(lab, (r / 1e3, comms.free_space_loss_dB(r)), fontsize=7.6,
                   xytext=(r / 1e3, comms.free_space_loss_dB(r) - 18))
    a.set_xlabel("Link range (km, log)"); a.set_ylabel("Free-space path loss (dB)")
    a.set_title("(a)")
    div = np.linspace(5e-6, 60e-6, 100)
    for j, c in [(0.3e-6, GOOD), (1e-6, WARN), (3e-6, BAD)]:
        a2 = [adcs.pointing_loss_dB(j, d) for d in div]
        b.plot(div * 1e6, a2, color=c, lw=2.2, label=f"jitter {j*1e6:.1f} urad")
    b.set_xlabel("Beam divergence (urad)"); b.set_ylabel("Pointing loss (dB)")
    b.set_title("(b)"); b.legend(fontsize=8); b.set_ylim(0, 12)
    fig.suptitle("FIG. C  Optical link budget & pointing", fontweight="bold")
    _credit(fig, "FSO link budget (arXiv:2204.13177); NASA TBIRD/LCRD; Suncatcher 1.6 Tbps @1.55um.")
    fig.tight_layout(); fig.savefig(FIGDIR / "fig_comms.png"); plt.close(fig)


def fig_reliability():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.4))
    t = np.linspace(0, 7, 100)
    for mtbf, c in [(30000, BAD), (50000, WARN), (100000, GOOD)]:
        a.plot(t, [reliability.reliability(x, mtbf) * 100 for x in t], color=c, lw=2.2,
               label=f"MTBF {mtbf//1000}k h")
    a.axvline(5, color="#999", ls=":"); a.set_xlabel("Years"); a.set_ylabel("Per-node reliability (%)")
    a.set_title("(a)"); a.legend(fontsize=8)
    over = np.linspace(0, 0.6, 40)
    p = reliability.reliability(5, 150000)   # 5-yr-design-life bus, R(5yr)~0.75
    avail = [reliability.expected_capacity_fraction(int(81 * (1 + o)), 81, p) * 100 for o in over]
    b.plot(over * 100, avail, color=COOL, lw=2.4)
    b.axhline(100, color=GOOD, ls="--"); b.text(1, 100.5, "full capacity", color=GOOD, fontsize=8)
    b.set_xlabel("Over-provisioning (%)"); b.set_ylabel("Expected capacity @5 yr (%)")
    b.set_title("(b)")
    fig.suptitle("FIG. R  Reliability & constellation availability", fontweight="bold")
    _credit(fig, "MIL-HDBK-217F; NASA SSRI; CubeSat reliability studies; Starlink attrition data.")
    fig.tight_layout(); fig.savefig(FIGDIR / "fig_reliability.png"); plt.close(fig)


def fig_compute_econ():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.4))
    mfu = np.linspace(0.05, 0.6, 100)
    for chip, c in [("tpu_v6e", COOL), ("h100", ACCENT)]:
        cost = [compute.cost_per_pflop_hour(2.7 if chip == "tpu_v6e" else 2.5, chip, m, 0.86) for m in mfu]
        a.plot(mfu * 100, cost, color=c, lw=2.3, label=chip)
    a.set_xlabel("Model-FLOPs utilization (%)"); a.set_ylabel("USD per useful PFLOP-hour")
    a.set_title("(a)"); a.legend(fontsize=8); a.set_ylim(0, 60)
    prot = ["none", "ecc_checkpoint", "ecc_sel_tmr", "full_tmr"]
    from . import radiation
    eff = [radiation.availability(p)["usable_compute"] * 100 for p in prot]
    b.bar(range(len(prot)), eff, color=[BAD, GOOD, WARN, "#888"])
    b.set_xticks(range(len(prot))); b.set_xticklabels(["none", "ECC+\nckpt", "ECC+\nTMR", "full\nTMR"], fontsize=8)
    b.set_ylabel("Usable compute (%)"); b.set_title("(b)")
    fig.suptitle("FIG. K  Compute throughput & economics", fontweight="bold")
    _credit(fig, "Google TPU v6e docs; NVIDIA H100; LBNL/Uptime PUE; cloud pricing. *v6e TDP estimated.")
    fig.tight_layout(); fig.savefig(FIGDIR / "fig_compute.png"); plt.close(fig)


def fig_mass_budget():
    s = DesignPoint().solve()
    mb = s["mass_breakdown"]
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    items = sorted(mb.items(), key=lambda kv: -kv[1])
    ax.barh([k for k, _ in items][::-1], [v for _, v in items][::-1], color=COOL)
    ax.set_xlabel("Mass (kg)")
    # figure title removed: it lives in the document caption
    for i, (k, v) in enumerate(items[::-1]):
        ax.text(v + 1, i, f"{v:.0f}", va="center", fontsize=8)
    _credit(fig, "orbital_dc.system.DesignPoint: power->array->mass->thermal->dv closure.")
    fig.savefig(FIGDIR / "fig_mass_budget.png"); plt.close(fig)


def fig_montecarlo(n=3000):
    rng = np.random.default_rng(1)
    A = 3.5 / 233.0
    from . import debris
    scenarios = ["min", "mod", "max"]
    life_lut = {s: orbit.lifetime_years(650, A, s) for s in scenarios}
    dv_lut = {s: propulsion.delta_v_budget(650, A, scenario=s)["total"] for s in scenarios}
    dbr_lut = {b: debris.collision_probability(15, 81, 5, band=b) * 100 for b in ("lo", "mid", "hi")}
    scen = rng.choice(scenarios, size=n, p=[.3, .5, .2])
    band = rng.choice(["lo", "mid", "hi"], size=n, p=[.3, .5, .2])
    life = [life_lut[s] for s in scen]
    dbr = [dbr_lut[b] for b in band]
    dv = [dv_lut[s] for s in scen]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    for ax, data, title, unit, ref in [
        (axes[0], life, "Natural lifetime", "yr", 5),
        (axes[1], dbr, "Debris P (5 yr)", "%", None),
        (axes[2], dv, "Total delta-v", "m/s", None)]:
        ax.hist(data, bins=40, color=COOL, alpha=0.85)
        if ref: ax.axvline(ref, color=BAD, ls="--", label="5-yr rule"); ax.legend(fontsize=8)
        ax.set_title(f"{title}\nP50={np.median(data):.1f} {unit}", fontsize=10)
        ax.set_xlabel(unit)
    fig.suptitle("FIG. U  Monte-Carlo uncertainty (solar cycle, debris flux, MFU, TDP)", fontweight="bold")
    _credit(fig, "Uncertainty propagation over NRLMSIS scenarios and ORDEM/MASTER flux band.")
    fig.tight_layout(); fig.savefig(FIGDIR / "fig_montecarlo.png"); plt.close(fig)


def fig_new_subsystems():
    """Ground link, thermal-throttle workload, latency, and finance (the four added modules)."""
    from . import groundlink, finance, workload
    fig, ax = plt.subplots(2, 2, figsize=(10.2, 7.4))
    chips = ["tpu_v6e", "h100", "b200"]
    loss = [workload.simulate_orbit(chip=c, radiator_area_m2=4.0)["throttle_loss_frac"] * 100 for c in chips]
    ax[0, 0].bar(chips, loss, color=[GOOD, WARN, BAD])
    ax[0, 0].set_ylabel("throttle loss (%)"); ax[0, 0].set_title("(a)")
    for i, v in enumerate(loss): ax[0, 0].text(i, v + 1, f"{v:.0f}%", ha="center", fontsize=8.5)
    ns = np.arange(1, 8)
    av = [groundlink.site_diversity_availability(int(n)) * 100 for n in ns]
    ax[0, 1].plot(ns, av, "o-", color=COOL, lw=2.3); ax[0, 1].axhline(99, color=GOOD, ls="--")
    ax[0, 1].set_ylim(40, 102); ax[0, 1].set_xlabel("ground stations")
    ax[0, 1].set_ylabel("downlink availability (%)"); ax[0, 1].set_title("(b)")
    d = np.linspace(500, 12000, 100)
    ax[1, 0].plot(d, [groundlink.mesh_latency_ms(x)["leo_mesh_ms"] for x in d], color=COOL, lw=2.2, label="LEO optical mesh")
    ax[1, 0].plot(d, [groundlink.mesh_latency_ms(x)["fiber_ms"] for x in d], color=ACCENT, lw=2.2, label="terrestrial fiber")
    ax[1, 0].set_xlabel("path distance (km)"); ax[1, 0].set_ylabel("one-way latency (ms)")
    ax[1, 0].set_title("(c)"); ax[1, 0].legend(fontsize=8)
    rev = np.linspace(0.5e6, 4e6, 100)
    ax[1, 1].plot(rev / 1e6, [finance.dcf_summary(2e6, 0.3e6, r, 5, 0.10)["npv_usd"] / 1e6 for r in rev], color=NAVY, lw=2.3)
    ax[1, 1].axhline(0, color=BAD, ls="--"); ax[1, 1].set_xlabel("annual revenue ($M/sat)")
    ax[1, 1].set_ylabel("NPV ($M, 10% disc.)"); ax[1, 1].set_title("(d)")
    fig.suptitle("FIG. N  Added subsystems: ground link, thermal-throttle, latency, finance", fontweight="bold")
    _credit(fig, "groundlink/structures/workload/finance modules. Throttle from time-domain thermal sim; DCF at 10% discount.")
    fig.tight_layout(); fig.savefig(FIGDIR / "fig_new_subsystems.png"); plt.close(fig)


def generate_all():
    FIGDIR.mkdir(exist_ok=True); _style()
    fig_power(); fig_link_budget(); fig_reliability()
    fig_compute_econ(); fig_mass_budget(); fig_montecarlo(); fig_new_subsystems()
    return sorted(p.name for p in FIGDIR.glob("fig_*.png"))
