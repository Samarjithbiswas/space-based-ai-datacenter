"""Additional explanatory figures for the expanded treatise. Generated from the model so
every curve is consistent with the equations. Output: report/figures2/*.png"""
import sys, numpy as np, matplotlib.pyplot as plt, matplotlib as mpl
from pathlib import Path
sys.path.insert(0, "../systems-model")
from orbital_dc import orbit, thermal, environment, comms, reliability, compute, finance, propulsion
from orbital_dc.constants import S0, R_E

mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.grid": True, "grid.color": "#e6e9ec",
    "figure.dpi": 135, "savefig.dpi": 165, "savefig.bbox": "tight", "legend.frameon": False})
NAVY, ACC, COOL, GOOD, WARN, BAD = "#16243a", "#c75c2e", "#2f6f8f", "#2e7d4f", "#caa12a", "#a3303a"
OUT = Path("figures2"); OUT.mkdir(exist_ok=True)
# Figure-level titles and source lines live in the document caption, not on the image.
import matplotlib.figure as _mfig
_mfig.Figure.suptitle = lambda self, *a, **k: None
def cred(fig, t): return

# F1 eclipse & beta geometry
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.2))
alts = np.linspace(400, 1000, 100)
a.plot(alts, [orbit.critical_beta(h) for h in alts], color=COOL, lw=2.4)
a.axvline(650, color="#999", ls=":"); a.set_xlabel("Altitude (km)"); a.set_ylabel("Critical beta angle (deg)")
a.set_title("(a)")
betas = np.linspace(0, 90, 200)
b.plot(betas, [orbit.eclipse_fraction(650, bb) * 100 for bb in betas], color=ACC, lw=2.4)
b.axvline(orbit.critical_beta(650), color=GOOD, ls="--"); b.set_xlabel("Beta angle (deg)")
b.set_ylabel("Eclipse fraction (%)"); b.set_title("(b)")
fig.suptitle("Fig. A1  Eclipse geometry and the dawn-dusk advantage", fontweight="bold")
cred(fig, "orbit.critical_beta / eclipse_fraction; geometry of Chapter 6.")
fig.tight_layout(); fig.savefig(OUT / "figA1_eclipse.png"); plt.close(fig)

# F2 view factor and external loads
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.2))
a.plot(alts, [environment.earth_view_factor(h) for h in alts], color=COOL, lw=2.4)
a.axvline(650, color="#999", ls=":"); a.set_xlabel("Altitude (km)"); a.set_ylabel("Earth view factor F")
a.set_title("(a)")
for asv, c, lab in [(0.15, COOL, "alpha_s=0.15"), (0.25, ACC, "alpha_s=0.25")]:
    loads = [environment.thermal_loads(h, 4.0, alpha_s=asv)["total"] for h in alts]
    b.plot(alts, loads, color=c, lw=2.2, label=lab)
b.set_xlabel("Altitude (km)"); b.set_ylabel("External load on 4 m^2 (W)")
b.set_title("(b)"); b.legend(fontsize=8)
fig.suptitle("Fig. A2  Environmental heat loads (Chapters 8, 10)", fontweight="bold")
cred(fig, "environment.earth_view_factor / thermal_loads; S0=1361 W/m^2, a=0.30, q_IR=237 W/m^2.")
fig.tight_layout(); fig.savefig(OUT / "figA2_loads.png"); plt.close(fig)

# F3 radiator equilibrium temperature & area vs operating temp
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.2))
flux = np.linspace(100, 1000, 100)
a.plot(flux, [(thermal.radiator_temperature(q * 4, 4.0, emissivity=0.85, sides=1)) for q in flux], color=COOL, lw=2.4)
a.set_xlabel("Heat flux (W/m^2)"); a.set_ylabel("Radiator temperature (C)")
a.set_title("(a)")
Ts = np.linspace(0, 80, 100)
b.plot(Ts, [thermal.radiator_area(1e6, T) for T in Ts], color=ACC, lw=2.4)
b.set_xlabel("Operating temperature (C)"); b.set_ylabel("Radiator area for 1 MW (m^2)")
b.set_title("(b)"); b.set_ylim(0, 2500)
fig.suptitle("Fig. A3  Radiator equilibrium and the area-temperature trade", fontweight="bold")
cred(fig, "thermal.radiator_temperature / radiator_area; Stefan-Boltzmann, Chapter 10.")
fig.tight_layout(); fig.savefig(OUT / "figA3_radiator.png"); plt.close(fig)

# F4 required Tx power vs range (FSO) and pointing-loss
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.2))
R = np.logspace(2, 7, 100)
a.loglog(R / 1e3, (R / 5.419e6) ** 2, color=COOL, lw=2.4)     # P to hold 3 dB margin (~R^2)
a.axhline(1.0, color=BAD, ls="--"); a.text(0.2, 1.2, "1 W terminal limit", color=BAD, fontsize=8)
a.axvline(5419, color=GOOD, ls=":"); a.text(5600, 1e-3, "5,419 km\nreliable limit", color=GOOD, fontsize=7.6)
a.set_xlabel("Link range (km, log)"); a.set_ylabel("Required Tx power (W, log)")
a.set_title("(a)")
from orbital_dc.adcs import pointing_loss_dB
div = np.linspace(5e-6, 40e-6, 100)
for j, c in [(0.3e-6, GOOD), (1e-6, WARN), (3e-6, BAD)]:
    b.plot(div * 1e6, [pointing_loss_dB(j, d) for d in div], color=c, lw=2.1, label=f"jitter {j*1e6:.1f} urad")
b.set_xlabel("Beam divergence (urad)"); b.set_ylabel("Pointing loss (dB)"); b.set_ylim(0, 12)
b.set_title("(b)"); b.legend(fontsize=8)
fig.suptitle("Fig. A4  Optical link: range and pointing (Chapters 13, 14)", fontweight="bold")
cred(fig, "Inverse-square margin scaling (arXiv:2204.13177); adcs.pointing_loss_dB.")
fig.tight_layout(); fig.savefig(OUT / "figA4_link.png"); plt.close(fig)

# F5 dose-depth (log) with thresholds
fig, ax = plt.subplots(figsize=(7.4, 4.4))
x = np.linspace(1, 20, 100)
ax.semilogy(x, [environment.tid_dose_rate(v) * 5 for v in x], color=COOL, lw=2.5, label="5-yr cumulative")
ax.axhline(2000, color=BAD, ls="--"); ax.text(11, 2300, "HBM first irregularities 2 krad", color=BAD, fontsize=8)
ax.axhline(15000, color="#b0506a", ls=":"); ax.text(11, 16500, "no hard failure to 15 krad", color="#b0506a", fontsize=8)
ax.axhline(750, color=GOOD, ls=":"); ax.text(11, 820, "5-yr requirement 750 rad", color=GOOD, fontsize=8)
ax.axvline(10, color="#999", ls=":"); ax.set_xlabel("Aluminium shielding (mm)")
ax.set_ylabel("Cumulative 5-yr TID rad(Si), log")  # title removed: lives in the document caption
cred(fig, "environment.tid_dose_rate; SHIELDOSE-2/AE8-AP8 class; thresholds per arXiv:2511.19468.")
fig.savefig(OUT / "figA5_dose.png"); plt.close(fig)

# F6 reliability families and k-of-n
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.2))
tt = np.linspace(0, 7, 100)
for m, c in [(50000, BAD), (100000, WARN), (200000, GOOD)]:
    a.plot(tt, [reliability.reliability(x, m) for x in tt], color=c, lw=2.2, label=f"MTBF {m//1000}k h")
a.axvline(5, color="#999", ls=":"); a.set_xlabel("Years"); a.set_ylabel("Per-node reliability")
a.set_title("(a)"); a.legend(fontsize=8)
p5 = reliability.reliability(5, 150000)
ov = np.linspace(0, 0.6, 50)
b.plot(ov * 100, [reliability.expected_capacity_fraction(int(81 * (1 + o)), 81, p5) * 100 for o in ov], color=COOL, lw=2.4)
b.axhline(100, color=GOOD, ls="--"); b.set_xlabel("Over-provisioning (%)")
b.set_ylabel("Capacity at 5 yr (%)"); b.set_title("(b)")
fig.suptitle("Fig. A6  Reliability and constellation availability (Chapter 16)", fontweight="bold")
cred(fig, "reliability.reliability / expected_capacity_fraction; exponential + binomial models.")
fig.tight_layout(); fig.savefig(OUT / "figA6_reliability.png"); plt.close(fig)

# F7 LCOE vs MFU and vs launch price
fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.2))
mfu = np.linspace(0.05, 0.6, 80)
for chip, c, hr in [("tpu_v6e", COOL, 2.7), ("h100", ACC, 2.5)]:
    a.plot(mfu * 100, [compute.cost_per_pflop_hour(hr, chip, m, 0.86) for m in mfu], color=c, lw=2.2, label=chip)
a.set_ylim(0, 60); a.set_xlabel("Model-FLOPs utilization (%)"); a.set_ylabel("USD per useful PFLOP-hr")
a.set_title("(a)"); a.legend(fontsize=8)
pk = np.array([3770, 1500, 600, 300, 150])
deliv = compute.delivered_pflops(4, "tpu_v6e", 0.30, 0.86)
lc = [finance.lcoe_per_pflop_hr(1.1e6 + p * 415, 0.15 * (1.1e6 + p * 415), deliv) for p in pk]
b.plot(pk, lc, "o-", color=NAVY, lw=2.2); b.invert_xaxis()
b.set_xlabel("Launch price (USD/kg, ->cheaper)"); b.set_ylabel("LCOE (USD/PFLOP-hr)")
b.set_title("(b)")
fig.suptitle("Fig. A7  Levelized cost of compute (Chapter 21)", fontweight="bold")
cred(fig, "compute.cost_per_pflop_hour / finance.lcoe_per_pflop_hr; discounted, Chapter 21.")
fig.tight_layout(); fig.savefig(OUT / "figA7_lcoe.png"); plt.close(fig)

# F8 mass pie
from orbital_dc.system import DesignPoint
s = DesignPoint().solve(); mb = s["mass_breakdown"]
fig, ax = plt.subplots(figsize=(6.6, 5.2))
items = sorted(mb.items(), key=lambda kv: -kv[1])
ax.pie([v for _, v in items], labels=[k for k, _ in items],
       autopct=lambda p: f"{p*sum(v for _,v in items)/100:.0f} kg", startangle=90,
       colors=plt.cm.tab20.colors, textprops={"fontsize": 8})
# figure title removed: it lives in the document caption
cred(fig, "system.DesignPoint mass closure (Chapter 12, 18).")
fig.savefig(OUT / "figA8_mass.png"); plt.close(fig)

print("wrote", sorted(p.name for p in OUT.glob("*.png")))
