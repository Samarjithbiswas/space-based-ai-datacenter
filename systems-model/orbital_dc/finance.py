"""Financial model: discounted cash flow (NPV, IRR), capital recovery, levelized cost of
compute (LCOE in $/PFLOP-hr), and reliability-driven replenishment OPEX.

This replaces the simple CAPEX + OPEX bookkeeping in `economics` with a proper
time-value-of-money treatment so the business case can be judged on NPV/IRR/LCOE.
"""
from __future__ import annotations
import numpy as np


def capital_recovery_factor(rate: float, years: int) -> float:
    """CRF = r(1+r)^n / ((1+r)^n - 1): annualizes a capital cost over its life."""
    if rate == 0:
        return 1.0 / years
    f = (1 + rate) ** years
    return float(rate * f / (f - 1))


def npv(rate: float, cashflows) -> float:
    """Net present value; cashflows[0] is year 0 (typically -CAPEX)."""
    return float(sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows)))


def irr(cashflows, lo=-0.9, hi=1.5, tol=1e-6) -> float:
    """Internal rate of return via bisection (NaN if no sign change in range)."""
    f_lo, f_hi = npv(lo, cashflows), npv(hi, cashflows)
    if f_lo * f_hi > 0:
        return float("nan")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_mid = npv(mid, cashflows)
        if abs(f_mid) < tol:
            return float(mid)
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return float(0.5 * (lo + hi))


def lcoe_per_pflop_hr(capex_usd: float, opex_yr_usd: float, delivered_pflops: float,
                      rate: float = 0.10, life_years: int = 5, utilization: float = 0.8) -> float:
    """Levelized cost of compute [$/PFLOP-hr]:
        (CRF * CAPEX + OPEX) / (annual useful PFLOP-hours)."""
    annual_pflop_hr = delivered_pflops * 8766.0 * utilization
    crf = capital_recovery_factor(rate, life_years)
    return float((crf * capex_usd + opex_yr_usd) / annual_pflop_hr)


def replenishment_opex(n_sats: int, sat_cost_usd: float, design_life_years: float) -> float:
    """Annual replenishment OPEX [$/yr] to sustain the fleet (~1/life replacement rate)."""
    return float(n_sats * sat_cost_usd / design_life_years)


def dcf_summary(capex_usd: float, opex_yr_usd: float, revenue_yr_usd: float,
                life_years: int = 5, rate: float = 0.10) -> dict:
    """Full discounted cash flow: NPV, IRR, simple payback."""
    net_yr = revenue_yr_usd - opex_yr_usd
    cashflows = [-capex_usd] + [net_yr] * life_years
    payback = capex_usd / net_yr if net_yr > 0 else float("inf")
    return {"npv_usd": npv(rate, cashflows), "irr": irr(cashflows),
            "annual_net_usd": net_yr, "payback_years": float(payback),
            "viable": npv(rate, cashflows) > 0}
