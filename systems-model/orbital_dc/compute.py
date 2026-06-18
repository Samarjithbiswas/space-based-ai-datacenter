"""Compute / workload model: delivered throughput, model-FLOPs-utilization (MFU),
radiation throughput tax, effective PUE, and cost per useful PFLOP-hour.
Sources: Google TPU v6e docs, NVIDIA datasheets, LBNL/Uptime PUE, cloud pricing.
"""
from __future__ import annotations

# Per-chip peak (BF16). TPU v6e TDP undisclosed -> estimate band.
PEAK_TFLOPS = {"tpu_v6e": 918.0, "h100": 989.0, "b200": 2250.0}
EST_TDP_W = {"tpu_v6e": 200.0, "h100": 700.0, "b200": 1000.0}   # *v6e estimated


def perf_per_watt(chip: str = "tpu_v6e") -> float:
    """Peak BF16 TFLOPS per watt (v6e uses an estimated TDP)."""
    return PEAK_TFLOPS[chip] / EST_TDP_W[chip]


def delivered_pflops(n_chips: int, chip: str = "tpu_v6e", mfu: float = 0.30,
                     radiation_availability: float = 0.86) -> float:
    """Useful delivered compute [PFLOPS] = peak * MFU * radiation availability."""
    peak_pflops = n_chips * PEAK_TFLOPS[chip] / 1e3
    return peak_pflops * mfu * radiation_availability


def effective_pue(compute_W: float, total_W: float, radiation_availability: float = 0.86) -> float:
    """Effective PUE including the radiation throughput tax (useful-work basis)."""
    return (total_W / compute_W) / radiation_availability


def cost_per_pflop_hour(chip_cost_usd_per_hr: float, chip: str = "tpu_v6e",
                        mfu: float = 0.30, radiation_availability: float = 0.86) -> float:
    """Cost per USEFUL PFLOP-hour given utilization and availability."""
    useful_pflops = PEAK_TFLOPS[chip] / 1e3 * mfu * radiation_availability
    return chip_cost_usd_per_hr / useful_pflops
