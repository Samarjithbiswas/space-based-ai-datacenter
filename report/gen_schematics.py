"""Additional schematic diagrams for chapters that lacked one, drawn with matplotlib and saved
straight to PNG (no SVG/browser step). Clean line art, navy/teal palette, no baked figure number
or source line (the caption lives in the document). Output: report/schematics/sch_*.png
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, FancyBboxPatch

mpl.rcParams.update({"font.family": "DejaVu Sans", "savefig.bbox": "tight", "savefig.dpi": 200})
NAVY, TEAL, ACC, SLATE, MUTE = "#16243a", "#0d7d74", "#c75c2e", "#26313f", "#5c6b7a"
LIGHT, EARTH = "#eef2f5", "#cfe0ea"
from pathlib import Path
OUT = Path(__file__).resolve().parent / "schematics"; OUT.mkdir(exist_ok=True)


def _ax(w=7.4, h=4.6):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_aspect("equal"); ax.axis("off"); return fig, ax


def save(fig, name):
    fig.savefig(OUT / name, facecolor="white", pad_inches=0.12); plt.close(fig)


def box(ax, x, y, w, h, t, fc=LIGHT, tc=NAVY, fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=NAVY, lw=1.1))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=tc)


def arrow(ax, p, q, c=SLATE, lw=1.4, style="-|>"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=13, color=c, lw=lw))


# 1. Ch4 -- orbit geometry (conic, elements)
fig, ax = _ax(7.6, 4.8)
a, e = 2.6, 0.5
th = np.linspace(0, 2 * np.pi, 400)
b = a * np.sqrt(1 - e ** 2)
ax.plot(a * np.cos(th) - a * e, b * np.sin(th), color=TEAL, lw=2.2)   # orbit, center shifted so focus at origin
ax.add_patch(Circle((0, 0), 0.34, fc=EARTH, ec=NAVY, lw=1.2)); ax.text(0, 0, "Earth", ha="center", va="center", fontsize=9)
# perigee (right), apogee (left)
ax.scatter([a - a * e], [0], s=20, color=NAVY); ax.text(a - a * e + 0.05, -0.28, "perigee", fontsize=9, color=SLATE)
ax.scatter([-a - a * e], [0], s=20, color=NAVY); ax.text(-a - a * e, -0.30, "apogee", ha="center", fontsize=9, color=SLATE)
# semi-major axis
ax.annotate("", (a - a * e, 0.0), (-a - a * e, 0.0), arrowprops=dict(arrowstyle="<->", color=MUTE, lw=1))
ax.text(-a * e, 0.16, "2a", ha="center", fontsize=10, color=MUTE)
# satellite at true anomaly
ta = 1.05
r = a * (1 - e ** 2) / (1 + e * np.cos(ta))
sx, sy = r * np.cos(ta), r * np.sin(ta)
ax.plot([0, sx], [0, sy], color=ACC, lw=1.6); ax.scatter([sx], [sy], s=42, color=ACC, zorder=5)
ax.text(sx + 0.06, sy + 0.05, "satellite", fontsize=9, color=ACC)
ax.text(0.55, 0.30, r"$r,\ \theta$", fontsize=11, color=ACC)
ax.text(0.30, 0.10, r"$\theta$", fontsize=11, color=ACC)
save(fig, "sch_orbit_geometry.png")

# 2. Ch7 -- orbital decay spiral
fig, ax = _ax(6.4, 5.0)
ax.add_patch(Circle((0, 0), 1.0, fc=EARTH, ec=NAVY, lw=1.2)); ax.text(0, 0, "Earth", ha="center", va="center", fontsize=9)
t = np.linspace(0, 6 * np.pi, 800)
r = 2.7 - 0.20 * t
m = r > 1.05
ax.plot(r[m] * np.cos(t[m]), r[m] * np.sin(t[m]), color=ACC, lw=1.8)
arrow(ax, (r[m][-1] * np.cos(t[m][-1]), r[m][-1] * np.sin(t[m][-1])), (1.02 * np.cos(t[m][-1]), 1.02 * np.sin(t[m][-1])), c=ACC)
ax.scatter([2.7], [0], s=42, color=TEAL, zorder=5); ax.text(2.78, 0.05, "start, 650 km", fontsize=9, color=TEAL)
ax.text(0, -3.05, "drag slowly removes orbital energy; the orbit spirals in", ha="center", fontsize=10, color=SLATE)
ax.text(0, -3.4, "natural lifetime about two decades at moderate solar activity", ha="center", fontsize=9.5, color=MUTE)
ax.set_xlim(-3, 3.2); ax.set_ylim(-3.6, 3)
save(fig, "sch_decay_spiral.png")

# 3. Ch11 -- power budget flow (dawn-dusk, mostly sunlit)
fig, ax = plt.subplots(figsize=(8.2, 3.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
ax.text(0.5, 3.5, "Sunlight", color=ACC, fontsize=11, fontweight="bold")
for y in (2.7, 2.1, 1.5):
    arrow(ax, (0.4, y), (1.5, y), c=ACC)
box(ax, 1.6, 1.5, 1.8, 1.2, "Solar array\n$\\eta\\approx0.28$ (EOL)", fc="#e3f1ef")
box(ax, 4.0, 1.5, 1.6, 1.2, "Power bus")
arrow(ax, (3.4, 2.1), (4.0, 2.1))
box(ax, 6.4, 2.6, 1.7, 0.9, "Compute", fc=LIGHT)
box(ax, 6.4, 1.5, 1.7, 0.9, "Avionics", fc=LIGHT)
box(ax, 6.4, 0.4, 1.7, 0.9, "Thermal / housekeeping", fc=LIGHT)
for yy in (3.05, 1.95, 0.85):
    arrow(ax, (5.6, 2.1), (6.4, yy))
box(ax, 4.05, 0.2, 1.5, 0.8, "Battery (small)", fc="#fdece8", fs=9)
arrow(ax, (4.8, 1.5), (4.8, 1.0), c=MUTE, style="<->")
ax.text(8.3, 2.0, ">95% sunlit\norbit: battery\nbarely used", fontsize=9.5, color=SLATE, va="center")
save(fig, "sch_power_budget.png")

# 4. Ch16 -- k-of-n redundancy and replenishment
fig, ax = plt.subplots(figsize=(8.0, 3.2)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
n = 6
for i in range(n):
    fc = "#e3f1ef" if i < 5 else "#fdece8"
    box(ax, 0.5 + i * 1.35, 2.1, 1.1, 0.9, f"sat {i+1}", fc=fc, fs=9)
ax.text(5.0, 3.5, "deploy n, require k of n  (here n=6, k=5)", ha="center", fontsize=10.5, color=NAVY)
ax.text(8.2, 2.55, "1 down", color=ACC, fontsize=9)
box(ax, 0.5 + 5 * 1.35, 0.5, 1.1, 0.9, "spare", fc=LIGHT, fs=9)
arrow(ax, (0.5 + 5 * 1.35 + 0.55, 1.4), (0.5 + 5 * 1.35 + 0.55, 2.1), c=TEAL)
ax.text(5.0, 0.7, "continuous replenishment at about 1/L per year (L = design life) holds capacity",
        ha="center", fontsize=9.5, color=SLATE)
save(fig, "sch_redundancy.png")

# 5. Ch18 -- integrated budget closure loop
fig, ax = plt.subplots(figsize=(7.4, 4.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 8)
nodes = {"Power": (4.2, 6.6), "Solar array area": (7.2, 5.2), "Mass / structure": (7.2, 2.6),
         "Thermal / radiator": (4.2, 1.2), "Propulsion Δv": (1.2, 2.6), "Compute load": (1.2, 5.2)}
for t, (x, y) in nodes.items():
    box(ax, x - 1.15, y - 0.5, 2.3, 1.0, t, fc=LIGHT, fs=9.5)
seq = ["Power", "Solar array area", "Mass / structure", "Thermal / radiator", "Propulsion Δv", "Compute load", "Power"]
for aN, bN in zip(seq, seq[1:]):
    ax.add_patch(FancyArrowPatch(nodes[aN], nodes[bN], arrowstyle="-|>", mutation_scale=13,
                                 color=TEAL, lw=1.3, shrinkA=26, shrinkB=26))
ax.text(4.2, 4.0, "iterate to a\nself-consistent\ndesign point", ha="center", va="center", fontsize=10, color=NAVY)
save(fig, "sch_budget_closure.png")

# 6. Ch28 -- Clohessy-Wiltshire relative motion (2:1 ellipse)
fig, ax = _ax(6.6, 4.2)
ph = np.linspace(0, 2 * np.pi, 300)
ax.plot(2 * np.sin(ph), np.cos(ph), color=TEAL, lw=2.2)        # 2:1 along-track:radial ellipse
ax.scatter([0], [0], s=60, marker="*", color=NAVY, zorder=5); ax.text(0.12, 0.06, "chief", fontsize=9, color=NAVY)
ax.scatter([2 * np.sin(1.0)], [np.cos(1.0)], s=40, color=ACC, zorder=5); ax.text(2 * np.sin(1.0) + 0.08, np.cos(1.0), "deputy", fontsize=9, color=ACC)
ax.annotate("", (2.3, 0), (-2.3, 0), arrowprops=dict(arrowstyle="->", color=MUTE, lw=1))
ax.annotate("", (0, -1.5), (0, 1.5), arrowprops=dict(arrowstyle="->", color=MUTE, lw=1))
ax.text(2.35, -0.18, "along-track", fontsize=9, color=MUTE, ha="right")
ax.text(0.08, 1.5, "radial", fontsize=9, color=MUTE)
ax.text(0, -1.95, "bounded relative motion traces a 2:1 ellipse (Clohessy-Wiltshire)", ha="center", fontsize=9.5, color=SLATE)
ax.set_xlim(-2.6, 2.6); ax.set_ylim(-2.2, 1.8)
save(fig, "sch_relative_motion.png")

print("wrote 6 schematics to", OUT)
