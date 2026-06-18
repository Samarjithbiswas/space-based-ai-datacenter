"""
Render each governing equation as a clean PNG for LinkedIn / slides.

WHY: LinkedIn posts and articles do not support LaTeX or MathJax. When you copy an
HTML page, the rendered math (SVG) does not paste. The reliable way to show real,
properly-typeset equations on LinkedIn is to insert them as images. This script
renders every equation to a high-resolution transparent-friendly PNG using
matplotlib's mathtext (no LaTeX installation required).

Output: report/equations/eq_XX_name.png  (white background, crisp, ready to upload)
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["mathtext.fontset"] = "cm"   # Computer Modern look
OUT = Path(__file__).resolve().parent / "equations"
OUT.mkdir(exist_ok=True)
INK = "#16243a"

# (filename, caption, mathtext-safe LaTeX)
EQS = [
    ("01_circular_speed", "Circular orbital speed", r"$v=\sqrt{\dfrac{\mu}{a}}$"),
    ("02_period", "Orbital period (Kepler)", r"$T=2\pi\sqrt{\dfrac{a^{3}}{\mu}}$"),
    ("03_sso_inclination", "Sun-synchronous inclination",
     r"$\cos i=-\dfrac{2\,\Omega_{sun}\,a^{2}}{3\,n\,J_{2}\,R_{E}^{2}}$"),
    ("04_critical_beta", "Critical beta angle (eclipse onset)",
     r"$\beta^{*}=\arcsin\!\dfrac{R_{E}}{R_{E}+h}$"),
    ("05_orbital_decay", "Orbital decay rate (drag)",
     r"$\dfrac{da}{dt}=-\,C_{D}\,\dfrac{A}{m}\,\rho(h)\,\sqrt{\mu\,a}$"),
    ("06_stefan_boltzmann", "Gray-body radiated power",
     r"$Q_{rad}=\varepsilon\,\sigma\,A\,\left(T^{4}-T_{\infty}^{4}\right)$"),
    ("07_radiator_area", "Required radiator area",
     r"$A_{rad}=\dfrac{Q}{\varepsilon\,\sigma\,T^{4}\,n_{s}\,(1-f_{p})}$"),
    ("08_junction_temp", "Junction temperature",
     r"$T_{j}=T_{rad}+Q\,R_{th}$"),
    ("09_eclipse_transient", "Eclipse transient (lumped capacitance)",
     r"$T(t)=T_{0}+\Delta T_{ss}\left(1-e^{-t/\tau}\right)$"),
    ("10_time_constant", "Thermal time constant",
     r"$\tau=\dfrac{m\,c_{p}}{h_{rad}\,A},\quad h_{rad}=4\varepsilon\sigma T_{0}^{3}$"),
    ("11_view_factor", "Earth view factor",
     r"$F=\dfrac{1}{2}\left[\,1-\sqrt{1-\left(\dfrac{R_{E}}{r}\right)^{2}}\,\right]$"),
    ("12_array_power", "Solar array power at the load",
     r"$P=S_{0}\,A\,\eta(T,\mathrm{life})\,\kappa_{pack}\,\eta_{path}$"),
    ("13_beam_divergence", "Diffraction-limited beam divergence",
     r"$\Theta\approx\dfrac{2.44\,\lambda}{D}$"),
    ("14_pointing_loss", "Optical pointing loss",
     r"$L_{point}=\exp\!\left(-\dfrac{2\,\theta_{err}^{2}}{\theta_{div}^{2}}\right)$"),
    ("15_telescope_gain", "Telescope (antenna) gain",
     r"$G=\left(\dfrac{\pi D}{\lambda}\right)^{2}$"),
    ("16_free_space_loss", "Free-space path loss",
     r"$L_{fs}=\left(\dfrac{4\pi R}{\lambda}\right)^{2}$"),
    ("17_dose_depth", "Ionizing dose vs shielding",
     r"$\dot{D}(x)=D_{0}\,e^{-x/\lambda}+D_{\infty}$"),
    ("18_debris_risk", "Catastrophic collision probability",
     r"$P=1-e^{-\Phi\,A\,N\,t}$"),
    ("19_cascade", "In-cluster cascade coupling",
     r"$P_{hit}=1-\exp\!\left(-\dfrac{N_{f}\,r_{t}^{2}}{4\,d^{2}}\right)$"),
    ("20_deorbit_dv", "Controlled de-orbit delta-v (Hohmann)",
     r"$\Delta v=v_{c1}\left(1-\sqrt{\dfrac{2\,r_{2}}{r_{1}+r_{2}}}\right)$"),
    ("21_rocket_eq", "Propellant mass (Tsiolkovsky)",
     r"$m_{p}=m_{dry}\left(e^{\,\Delta v/(I_{sp}\,g_{0})}-1\right)$"),
    ("22_reliability", "Exponential reliability",
     r"$R(t)=e^{-t/\mathrm{MTBF}}$"),
    ("23_k_of_n", "k-of-n redundancy",
     r"$R_{sys}=\sum_{i=k}^{n}\dfrac{n!}{i!\,(n-i)!}\,p^{i}(1-p)^{n-i}$"),
    ("24_effective_pue", "Effective PUE (with radiation tax)",
     r"$\mathrm{PUE}_{eff}=\dfrac{P_{total}/P_{compute}}{a_{r}}$"),
    ("25_launch_crossover", "Launch-cost cross-over",
     r"$p^{*}=\dfrac{C_{hw}}{m_{launch}}$"),
]


def render(name, latex, dpi=220):
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0.5, 0.5, latex, ha="center", va="center", fontsize=26, color=INK)
    fig.savefig(OUT / f"eq_{name}.png", dpi=dpi, bbox_inches="tight",
                pad_inches=0.18, facecolor="white", transparent=False)
    plt.close(fig)


if __name__ == "__main__":
    for fname, _cap, latex in EQS:
        render(fname, latex)
    # write a small index so the captions are obvious when inserting into LinkedIn
    idx = OUT / "INDEX.md"
    idx.write_text("# Equation images (for LinkedIn / slides)\n\n"
                   "Insert these PNGs where each equation appears in the article.\n\n"
                   + "\n".join(f"- `eq_{f}.png` — {c}" for f, c, _ in EQS) + "\n",
                   encoding="utf-8")
    print(f"Rendered {len(EQS)} equation images to {OUT}")
