"""
Launch-cost-parity prediction with Monte-Carlo sensitivity.

The Suncatcher paper projects LEO launch reaching <=$200/kg by ~2035 (a ~20% learning
rate, ~370,000 t additional cumulative mass, ~1800 Starship launches), at which point the
annualized launched-power price (~$810/kW/yr) approaches terrestrial data-center power spend
($570-3,000/kW/yr). The deep-research synthesis flagged this forecast as vendor-projected and
"highly sensitive to chosen initial conditions" -- so we generate the credibility band
ourselves rather than inherit a single number.

Model: a Wright learning curve on cumulative launched mass,
    price(M) = P0 * (M/M0)^b ,  b = log2(1 - LR)
with cumulative mass driven by a logistic ramp in Starship cadence. Monte-Carlo over the
unproven assumptions (learning rate, 2026 price, peak cadence, payload) yields the
distribution of the year LEO launch first reaches $200/kg.

Sources: arXiv:2511.19468 (Suncatcher cost model); SpaceX learning-rate analyses.
Output: report/figures_pred/fig_cost_parity.png  + printed P5/P50/P95 parity year.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5,
    "axes.titlesize": 11.5, "axes.titleweight": "bold", "axes.grid": True,
    "grid.color": "#e6e9ec", "figure.dpi": 135, "savefig.dpi": 165, "savefig.bbox": "tight",
    "legend.frameon": False})
NAVY, ACCENT, COOL, GOOD, BAD = "#16243a", "#c75c2e", "#2f6f8f", "#2e7d4f", "#a3303a"
OUT = Path(__file__).resolve().parent / "figures_pred"; OUT.mkdir(exist_ok=True)

YEARS = np.arange(2026, 2051)
PARITY = 200.0          # USD/kg target
FLOOR = 30.0            # marginal cost floor


def price_path(P0, LR, payload_t, peak_cad, M0=3000.0, t_mid=2030.0, k=1.3, years=None):
    """Return price(t) over `years` (default YEARS) for one parameter set."""
    yr = YEARS if years is None else years
    b = np.log2(1 - LR)
    cad = peak_cad / (1 + np.exp(-(yr - t_mid) / k))         # launches/yr (logistic)
    annual_mass = payload_t * cad
    cum = M0 + np.cumsum(annual_mass)                         # cumulative launched mass [t]
    price = P0 * (cum / M0) ** b
    return np.maximum(price, FLOOR)


def parity_year(price, years=None):
    yr = YEARS if years is None else years
    idx = np.where(price <= PARITY)[0]
    return yr[idx[0]] if len(idx) else np.nan


def monte_carlo(n=20000, seed=7, years=None):
    rng = np.random.default_rng(seed)
    LR = rng.uniform(0.15, 0.25, n)            # learning rate
    P0 = rng.uniform(1200, 3500, n)            # 2026 effective $/kg
    payload = rng.uniform(150, 250, n)         # Starship payload [t]
    peak = rng.uniform(80, 220, n)             # peak launches/yr
    yrs, paths = [], []
    for i in range(n):
        p = price_path(P0[i], LR[i], payload[i], peak[i], years=years)
        yrs.append(parity_year(p, years=years))
        if i < 400:
            paths.append(p)
    yrs = np.array(yrs, float)
    return yrs, np.array(paths)


def horizon_sensitivity():
    """Reach fraction and conditional median when the horizon is extended to 2060."""
    yrs, _ = monte_carlo(years=np.arange(2026, 2061))
    valid = yrs[~np.isnan(yrs)]
    return float(np.mean(~np.isnan(yrs))), float(np.median(valid))


def main():
    yrs, paths = monte_carlo()
    valid = yrs[~np.isnan(yrs)]
    pct = {p: float(np.percentile(valid, p)) for p in (5, 50, 95)}
    frac_2035 = float(np.mean(valid <= 2035))
    reach_frac = float(np.mean(~np.isnan(yrs)))   # fraction that reach parity within the 2050 horizon

    fig, (a, b) = plt.subplots(1, 2, figsize=(10.2, 4.6))
    # (a) price fan chart
    lo = np.percentile(paths, 5, axis=0); md = np.percentile(paths, 50, axis=0)
    hi = np.percentile(paths, 95, axis=0)
    a.fill_between(YEARS, lo, hi, color=COOL, alpha=0.18, label="5-95% band")
    a.plot(YEARS, md, color=COOL, lw=2.6, label="median path")
    a.axhline(PARITY, color=BAD, ls="--", lw=1.4); a.text(2026.2, PARITY*1.12, "$200/kg parity", color=BAD, fontsize=8.5)
    a.set_yscale("log"); a.set_xlabel("Year"); a.set_ylabel("LEO launch price (USD/kg, log)")
    a.set_title("(a)"); a.legend(fontsize=8.3, loc="upper right")
    # (b) parity-year histogram
    b.hist(valid, bins=np.arange(2030, 2051)-0.5, color=ACCENT, alpha=0.85)
    for p, c in [(5, GOOD), (50, NAVY), (95, BAD)]:
        b.axvline(pct[p], color=c, ls="--", lw=1.3)
    b.set_xlabel("Year LEO launch reaches $200/kg"); b.set_ylabel("Monte-Carlo count")
    b.set_title("(b)")
    # figure number and source line removed: they live in the document caption
    fig.tight_layout(); fig.savefig(OUT / "fig_cost_parity.png"); plt.close(fig)

    print("=" * 64)
    print(" LAUNCH-COST PARITY ($200/kg)  -  Monte-Carlo (n=20000)")
    print("=" * 64)
    print(f"  Scenarios reaching $200/kg by 2050 = {reach_frac*100:.0f}%  ({(1-reach_frac)*100:.0f}% never reach it)")
    print(f"  Conditional parity year   P5 = {pct[5]:.0f}   P50 = {pct[50]:.0f}   P95 = {pct[95]:.0f}")
    print(f"  P(parity by 2035) = {frac_2035*100:.0f}%")
    reach_2060, med_2060 = horizon_sensitivity()
    print(f"  Extending horizon to 2060: reach = {reach_2060*100:.0f}%, conditional median = {med_2060:.0f}")
    print(f"  (Suncatcher headline: '<=$200/kg by ~2035')")
    print("=" * 64)
    return pct, frac_2035, reach_frac


if __name__ == "__main__":
    main()
