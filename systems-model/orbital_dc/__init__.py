"""
orbital_dc - Space-Based AI Data Center Systems Model
=====================================================

A modular, fully-sourced, first-order systems engineering model for orbital AI compute
clusters. Each subsystem is an importable module of pure, documented physics functions;
`system.DesignPoint` closes them into one consistent design; `montecarlo` propagates
uncertainty. Reference architecture: Google Project Suncatcher (arXiv:2511.19468).

Subsystems (17)
---------------
constants, environment, orbit, thermal, power, adcs, comms, groundlink, structures,
radiation, debris, propulsion, reliability, compute, workload, finance, economics,
plus system (integration), montecarlo, figures

Quick start
-----------
    from orbital_dc.system import DesignPoint, constellation
    DesignPoint(n_chips=4, chip="tpu_v6e").solve()
    constellation()

Author: Samarjith Biswas, PhD   License: MIT
"""
from . import (constants, environment, orbit, thermal, power, adcs, comms, groundlink,
               structures, radiation, debris, propulsion, reliability, compute, workload,
               finance, economics, system, montecarlo)

__version__ = "1.1.0"
__all__ = ["constants", "environment", "orbit", "thermal", "power", "adcs", "comms",
           "groundlink", "structures", "radiation", "debris", "propulsion", "reliability",
           "compute", "workload", "finance", "economics", "system", "montecarlo", "figures"]
