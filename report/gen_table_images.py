"""Render the nomenclature and physical-constants tables as clean PNG images for the document and slides,
so math symbols do not break on paste. Manual text layout (no cell clipping); symbols use
mathtext; units use Unicode superscripts. High resolution, white and transparent copies."""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle

mpl.rcParams["mathtext.fontset"] = "cm"
OUT = Path(__file__).resolve().parent / "equations"; OUT.mkdir(exist_ok=True)
NAVY = "#16243a"; SOFT = "#f1efe9"; INK = "#1c1c1c"

_SUP = {"^3": "³", "^2": "²", "^4": "⁴", "^-2": "⁻²",
        "^-1": "⁻¹", "^-8": "⁻⁸", "^14": "¹⁴",
        "^-3": "⁻³"}
def units(s):
    for k, v in _SUP.items():
        s = s.replace(k, v)
    return s

NOMEN = [
    (r"$\mu$", "Earth gravitational parameter", "m^3/s^2"),
    (r"$R_E$", "Earth mean radius", "m"),
    (r"$J_2$", "Earth oblateness coefficient", "-"),
    (r"$a,\ h,\ r$", "semi-major axis, altitude, orbital radius", "m"),
    (r"$v,\ n,\ T$", "speed, mean motion, period", "m/s, rad/s, s"),
    (r"$\mathcal{E}$", "specific orbital energy", "J/kg"),
    (r"$\rho$", "neutral atmospheric density", "kg/m^3"),
    (r"$C_D,\ A/m$", "drag coefficient, area-to-mass ratio", "-, m^2/kg"),
    (r"$\sigma,\ \varepsilon,\ \alpha_s$", "Stefan-Boltzmann const., emissivity, solar absorptivity", "-"),
    (r"$T,\ Q,\ R_{th}$", "temperature, heat load, thermal resistance", "K, W, K/W"),
    (r"$S_0,\ F,\ a_{alb}$", "solar constant, view factor, Bond albedo", "W/m^2, -, -"),
    (r"$\Phi,\ N_f,\ r_t$", "debris flux, fragment count, target radius", "1/m^2/yr, -, m"),
    (r"$\Delta v,\ I_{sp}$", "velocity increment, specific impulse", "m/s, s"),
    (r"$G,\ L_{fs}$", "telescope gain, free-space path loss", "dB"),
    (r"$\lambda,\ D$", "wavelength, aperture diameter", "m"),
    (r"$\mathrm{MTBF},\ R(t)$", "mean time between failures, reliability", "h, -"),
    (r"$\eta,\ \mathrm{MFU}$", "efficiency, model-FLOPs utilization", "-"),
    (r"$r,\ \mathrm{CRF}$", "discount rate, capital-recovery factor", "-"),
]
CONST = [
    (r"$\mu$", "3.986004418 x 10^14 m^3/s^2"),
    (r"$R_E$", "6.371 x 10^6 m"),
    (r"$J_2$", "1.08263 x 10^-3"),
    (r"$\sigma$", "5.670374 x 10^-8 W/m^2/K^4"),
    (r"$g_0$", "9.80665 m/s^2"),
    (r"$S_0$", "1361 W/m^2 (modern TSIS-1; 1367 older WRC)"),
    (r"$T_{CMB}$", "2.725 K"),
    (r"$a_{alb},\ q_{IR}$", "0.30, 237 W/m^2"),
]


def render(rows, headers, xcols, fname, fig_w=10.6, fontsize=13, sym_fs=17):
    n = len(rows) + 1
    row_h = 0.5                      # inches per row
    fig_h = row_h * n + 0.2
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, 1); ax.set_ylim(0, n); ax.axis("off"); ax.invert_yaxis()
    # header band
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=NAVY, edgecolor="none"))
    for x, htxt in zip(xcols, headers):
        ax.text(x, 0.5, htxt, color="white", fontsize=fontsize + 1, fontweight="bold",
                va="center", ha="left")
    # data rows
    for i, row in enumerate(rows, start=1):
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, i), 1, 1, facecolor=SOFT, edgecolor="none"))
        for j, (x, val) in enumerate(zip(xcols, row)):
            txt = units(val) if j == len(xcols) - 1 else val
            ax.text(x, i + 0.5, txt, color=(NAVY if j == 0 else INK),
                    fontsize=(sym_fs if j == 0 else fontsize), va="center", ha="left",
                    clip_on=False)
    # thin horizontal rules
    for i in range(n + 1):
        ax.plot([0, 1], [i, i], color="#d9dde1", lw=0.6)
    fig.savefig(OUT / fname, dpi=300, bbox_inches="tight", pad_inches=0.10, facecolor="white")
    fig.savefig(OUT / fname.replace(".png", "_transparent.png"), dpi=300,
                bbox_inches="tight", pad_inches=0.10, transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    render(NOMEN, ["Symbol", "Meaning", "Units"], [0.015, 0.20, 0.74], "table_nomenclature.png")
    render(CONST, ["Constant", "Value"], [0.015, 0.20], "table_constants.png", fig_w=9.0)
    print("wrote table_nomenclature.png and table_constants.png (white + transparent)")
