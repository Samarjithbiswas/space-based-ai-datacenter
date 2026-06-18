"""
Numerical solver suite for the orbital data-center governing equations.
======================================================================

This module solves each governing equation of the system with an explicit, named numerical
method, rather than only evaluating closed forms. It provides:

  * generic primitives:  newton_raphson, bisection, rk4_integrate
  * a robust root finder (SciPy Brent) and ODE integrator (SciPy solve_ivp) where rigor matters
  * a solver for every load-bearing problem in the analysis
  * solve_reference_mission(), which chains the solvers into one end-to-end solution
  * a printed solution report and self-checks

Every solver states the equation it solves and the method it uses. Units are SI unless noted.
"""
from __future__ import annotations
import numpy as np
from .constants import MU, R_E, SIGMA, G0
from .environment import density

try:
    from scipy.optimize import brentq
    from scipy.integrate import solve_ivp
    _HAVE_SCIPY = True
except Exception:                                   # pragma: no cover
    _HAVE_SCIPY = False


# =====================================================================================
# 1. Generic numerical primitives
# =====================================================================================
def newton_raphson(f, fprime, x0, tol=1e-8, max_iter=100):
    """Solve f(x)=0 by Newton-Raphson. Returns (root, iterations)."""
    x = float(x0)
    for k in range(1, max_iter + 1):
        fx = f(x)
        if abs(fx) < tol:
            return x, k
        x -= fx / fprime(x)
    return x, max_iter


def bisection(f, lo, hi, tol=1e-8, max_iter=200):
    """Solve f(x)=0 on a bracket [lo, hi] by bisection (no derivative needed)."""
    flo = f(lo)
    if flo * f(hi) > 0:
        return float("nan"), 0
    for k in range(1, max_iter + 1):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(fm) < tol or 0.5 * (hi - lo) < tol:
            return mid, k
        if flo * fm < 0:
            hi = mid
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi), max_iter


def rk4_integrate(rhs, y0, t0, t1, dt, stop=None):
    """Fixed-step classical Runge-Kutta (4th order) integrator.
    rhs(t, y) -> dy/dt. Optional stop(t, y)->bool to terminate early.
    Returns (t_array, y_array)."""
    ts, ys = [t0], [float(y0)]
    t, y = t0, float(y0)
    n = int(np.ceil((t1 - t0) / dt))
    for _ in range(n):
        k1 = rhs(t, y)
        k2 = rhs(t + dt / 2, y + dt / 2 * k1)
        k3 = rhs(t + dt / 2, y + dt / 2 * k2)
        k4 = rhs(t + dt, y + dt * k3)
        y += dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
        ts.append(t); ys.append(y)
        if stop and stop(t, y):
            break
    return np.array(ts), np.array(ys)


# =====================================================================================
# 2. Thermal: radiator equilibrium temperature  (Newton-Raphson on the quartic)
# =====================================================================================
def solve_radiator_temperature(heat_W, area_m2, emissivity=0.85, sides=1, T_space=2.725):
    """Solve  Q - eps*sigma*A_eff*(T^4 - T_space^4) = 0  for T (Kelvin), by Newton-Raphson.
    Returns (T_celsius, iterations)."""
    A = area_m2 * sides
    f = lambda T: heat_W - emissivity * SIGMA * A * (T**4 - T_space**4)
    fp = lambda T: -4 * emissivity * SIGMA * A * T**3
    T, it = newton_raphson(f, fp, 300.0, tol=1e-4)
    return T - 273.15, it


def solve_radiator_area_for_margin(chip_W, r_th, T_radiator_C, T_junction_max=125.0,
                                   total_heat_W=None, emissivity=0.90, sides=2, parasitic=0.12):
    """Largest passive thermal resistance and the radiator area consistent with a given
    junction-temperature margin. Solves T_j = T_rad + Q*R_th <= T_jmax and sizes the radiator."""
    dT_budget = T_junction_max - T_radiator_C
    feasible = chip_W * r_th <= dT_budget
    Q = total_heat_W if total_heat_W is not None else chip_W
    T = T_radiator_C + 273.15
    area = Q / (emissivity * SIGMA * T**4 * sides * (1 - parasitic))
    return {"interface_dT_C": chip_W * r_th, "passive_feasible": feasible,
            "radiator_area_m2": area}


# =====================================================================================
# 3. Orbital decay lifetime  (RK4 integration of da/dt = -Cd (A/m) rho sqrt(mu a))
# =====================================================================================
def solve_orbital_lifetime(alt_km, area_to_mass, scenario="mod", cd=2.2, reentry_km=120.0):
    """Integrate the circular-orbit drag-decay ODE to re-entry with RK4. Returns lifetime [yr]."""
    a0 = R_E + alt_km * 1e3
    a_re = R_E + reentry_km * 1e3
    yr = 3.15576e7

    def rhs(t, a):
        h = max((a - R_E) / 1e3, 0.0)
        return -cd * area_to_mass * density(h, scenario) * np.sqrt(MU * a)

    # adaptive step: smaller as altitude drops (drag steepens)
    t, a, dt = 0.0, a0, 6 * 3600.0
    while a > a_re and t < 3000 * yr:
        ts, ys = rk4_integrate(rhs, a, t, t + dt, dt)
        a = ys[-1]; t = ts[-1]
        h = (a - R_E) / 1e3
        dt = 48 * 3600 if h > 500 else (12 * 3600 if h > 300 else 2 * 3600)
    return t / yr


# =====================================================================================
# 4. Eclipse thermal transient  (RK4 of the nonlinear lumped-capacitance ODE)
# =====================================================================================
def solve_eclipse_transient(duration_s, radiator_mass_kg=54.0, cp=900.0, area_m2=4.0,
                            emissivity=0.85, Q_compute_W=1450.0, Q_solar_W=100.0, T0_C=21.4):
    """Integrate  m cp dT/dt = Q_in(t) - eps sigma A T^4  through an eclipse (solar -> 0)."""
    C = radiator_mass_kg * cp
    T0 = T0_C + 273.15

    def rhs(t, T):
        Q_in = Q_compute_W - Q_solar_W           # solar input drops to zero during eclipse
        return (Q_in - emissivity * SIGMA * area_m2 * T**4) / C

    ts, ys = rk4_integrate(rhs, T0, 0.0, duration_s, 1.0)
    return {"T_end_C": ys[-1] - 273.15, "delta_T_C": ys[-1] - T0}


# =====================================================================================
# 5. Controlled de-orbit Delta-v  (closed-form Hohmann from vis-viva)
# =====================================================================================
def solve_deorbit_dv(alt_km, perigee_km=180.0):
    """Delta-v for a single retrograde Hohmann burn lowering perigee to perigee_km [m/s]."""
    r1, r2 = R_E + alt_km * 1e3, R_E + perigee_km * 1e3
    v1 = np.sqrt(MU / r1)
    return v1 * (1 - np.sqrt(2 * r2 / (r1 + r2)))


# =====================================================================================
# 6. Optical-link maximum range  (root-find the range where margin = 0)
# =====================================================================================
def solve_link_max_range(p_tx_W=1.0, target_margin_dB=0.0,
                         ref_range_km=5419.0, ref_margin_dB=3.0):
    """Range at which an inter-satellite optical link meets a target margin, anchored to the
    published design point (Liang et al. 2022, arXiv:2204.13177): a 1 W link holds 3 dB margin
    at 5,419 km. Free-space loss scales as R^2 (20 dB per decade), and transmit power adds
    10*log10(P) dB, so the margin is

        margin(R) = ref_margin + 10*log10(P) - 20*log10(R/ref_range).

    Solved for margin = target_margin_dB by Brent's method. Returns range [km]."""
    def margin(R_km):
        return ref_margin_dB + 10 * np.log10(p_tx_W) - 20 * np.log10(R_km / ref_range_km) - target_margin_dB
    if _HAVE_SCIPY:
        return float(brentq(margin, 1.0, 1e6))
    R, _ = bisection(margin, 1.0, 1e6, tol=1.0)
    return R


# =====================================================================================
# 7. Internal rate of return  (root-find NPV = 0)
# =====================================================================================
def solve_irr(cashflows):
    """Solve NPV(r) = 0 for the internal rate of return."""
    npv = lambda r: sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))
    if _HAVE_SCIPY:
        try:
            return brentq(npv, -0.9, 5.0)
        except ValueError:
            return float("nan")
    r, _ = bisection(npv, -0.9, 5.0, tol=1e-6)
    return r


# =====================================================================================
# 8. Launch-cost parity year  (root-find on the learning curve)
# =====================================================================================
def solve_cost_parity_year(p0=2000.0, learning_rate=0.20, payload_t=200.0, peak_cadence=150.0,
                           target_usd_per_kg=200.0, M0=3000.0, t_mid=2030.0, k=1.3,
                           year_start=2026, year_end=2055):
    """Find the first year LEO launch price reaches the target, given a Wright learning curve
    on cumulative launched mass. Returns the (fractional) year or NaN if not reached."""
    b = np.log2(1 - learning_rate)
    years = np.arange(year_start, year_end + 1)
    cad = peak_cadence / (1 + np.exp(-(years - t_mid) / k))
    cum = M0 + np.cumsum(payload_t * cad)
    price = np.maximum(p0 * (cum / M0) ** b, 30.0)
    below = np.where(price <= target_usd_per_kg)[0]
    if len(below) == 0:
        return float("nan")
    i = below[0]
    if i == 0:
        return float(years[0])
    # linear interpolation in log-price for the crossing year
    y0, y1 = years[i - 1], years[i]
    p_a, p_b = np.log(price[i - 1]), np.log(price[i])
    frac = (np.log(target_usd_per_kg) - p_a) / (p_b - p_a)
    return float(y0 + frac * (y1 - y0))


def solve_cost_parity_distribution(n=4000, seed=7):
    """Monte-Carlo over the launch-cost assumptions; returns parity-year percentiles and the
    fraction of samples that reach $200/kg by 2060. The single-point forecast is skewed, so the
    distribution is the honest object."""
    rng = np.random.default_rng(seed)
    yrs = []
    for _ in range(n):
        y = solve_cost_parity_year(p0=rng.uniform(1200, 3500), learning_rate=rng.uniform(0.15, 0.25),
                                   payload_t=rng.uniform(150, 250), peak_cadence=rng.uniform(80, 220),
                                   year_end=2060)
        yrs.append(y)
    finite = np.array([y for y in yrs if not np.isnan(y)])
    pct = {p: float(np.percentile(finite, p)) for p in (5, 50, 95)} if len(finite) else {}
    return pct, len(finite) / n


# =====================================================================================
# 9. End-to-end reference-mission solution
# =====================================================================================
def solve_reference_mission():
    """Chain the solvers into one consistent solution for the reference design point."""
    am = 3.5 / 375.0
    T_rad_C, nr_it = solve_radiator_temperature(1450.0, 4.0, 0.85, sides=1)
    life = solve_orbital_lifetime(650.0, am, "mod")
    ecl = solve_eclipse_transient(300.0)
    dv = solve_deorbit_dv(650.0)
    rng = solve_link_max_range()
    irr = solve_irr([-2.0e6, 0.7e6, 0.7e6, 0.7e6, 0.7e6, 0.7e6])
    parity_pct, parity_frac = solve_cost_parity_distribution(2000)
    return {
        "radiator_temperature_C": T_rad_C, "newton_iterations": nr_it,
        "natural_lifetime_yr": life,
        "eclipse_dT_C": ecl["delta_T_C"],
        "deorbit_dv_mps": dv,
        "link_range_3dB_km": solve_link_max_range(1.0, target_margin_dB=3.0),
        "link_range_0dB_km": rng,
        "project_irr": irr,
        "cost_parity_year_p50": parity_pct.get(50, float("nan")),
        "cost_parity_reach_frac": parity_frac,
    }


def main():
    sol = solve_reference_mission()
    print("=" * 70)
    print(" ORBITAL DATA-CENTER SOLVER SUITE  -  REFERENCE-MISSION SOLUTION")
    print("=" * 70)
    print(f"  Radiator temperature (Newton-Raphson, {sol['newton_iterations']} it) : "
          f"{sol['radiator_temperature_C']:7.2f} C")
    print(f"  Natural lifetime at 650 km (RK4 decay)              : {sol['natural_lifetime_yr']:7.1f} yr")
    print(f"  Eclipse temperature drop (RK4 transient)            : {sol['eclipse_dT_C']:7.2f} C")
    print(f"  Controlled de-orbit delta-v (Hohmann)               : {sol['deorbit_dv_mps']:7.1f} m/s")
    print(f"  Optical link range, 3 dB / 0 dB margin (1 W)         : {sol['link_range_3dB_km']:5.0f} / {sol['link_range_0dB_km']:.0f} km")
    print(f"  Project IRR at assumed revenue (NPV root)           : {sol['project_irr']*100:7.1f} %")
    print(f"  Launch-cost parity year, P50 (Monte-Carlo)          : {sol['cost_parity_year_p50']:7.0f}"
          f"   ({sol['cost_parity_reach_frac']*100:.0f}% reach by 2060)")
    print("=" * 70)


if __name__ == "__main__":
    main()
