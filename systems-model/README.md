# orbital_dc — Space-Based AI Data Center Systems Model

A modular, fully-sourced, end-to-end **systems-engineering** model for orbital AI compute
clusters. It is the complete continuation of the *Space-Based AI Data Centers* study: where
Part I covered thermal control and the survivability companion added debris/radiation/disposal,
this package models **every subsystem** and closes them into one self-consistent design.

Reference architecture: Google **Project Suncatcher** ([arXiv:2511.19468](https://arxiv.org/abs/2511.19468)).

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![tests](https://img.shields.io/badge/pytest-108_passing-success) ![validation](https://img.shields.io/badge/validation-23%2F23-success) ![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue) ![pip](https://img.shields.io/badge/install-pip%20install%20-e%20.-informational) ![modules](https://img.shields.io/badge/subsystems-17-informational)

```python
from orbital_dc.system import DesignPoint, constellation
DesignPoint(n_chips=4, chip="tpu_v6e", alt_km=650).solve()   # one self-consistent satellite
constellation()                                              # aggregate to 81-sat cluster
```

---

## Why this exists

Part I answered "can the chip stay cool?" (yes). The survivability work answered "will it survive
and de-orbit?" (debris and disposal are the hard parts). Neither modeled the **rest of the
spacecraft**. This package completes the picture by adding the missing subsystems and, crucially,
an **integration layer** that makes power, mass, thermal, propulsion, reliability, and economics
close on each other instead of being analyzed in isolation.

## Subsystem modules (each is pure, documented, independently testable)

| Module | Models | Key sources |
|---|---|---|
| `constants` | physical + program constants | IERS, CODATA, Suncatcher paper |
| `environment` | NRLMSIS atmosphere, solar/albedo/IR loads, debris flux, TID, SEU | NRLMSIS 2.1, ORDEM/MASTER, SHIELDOSE-2 |
| `orbit` | Kepler, SSO inclination, eclipse/beta, J2, drag decay, **Clohessy-Wiltshire** relative dynamics | standard astrodynamics |
| `thermal` | radiator sizing, resistance network, transient eclipse, **exact Part I reproduction** | Stefan-Boltzmann, Gilmore |
| `power` | triple-junction array (BOL/EOL + temp derate), Li-ion battery, EPS budget | Azur/Spectrolab, NASA SoA |
| `adcs` | optical pointing budget, beam divergence, reaction-wheel/star-tracker limits, disturbance torques | SDA OCT, GRACE-FO, Mynaric/TESAT |
| `comms` | FSO link budget (ISL + ground), latency, fabric capacity | NASA TBIRD/LCRD, arXiv:2204.13177 |
| `groundlink` | sat-to-ground optical downlink, slant atmospheric loss, cloud site-diversity availability, contact geometry, mesh-vs-fiber latency | NASA TBIRD; FSO link literature |
| `structures` | inertia tensor from geometry, structural mass from launch loads, panel modal frequency | spacecraft structural design |
| `workload` | time-domain coupled thermal-throttle compute (delivered PFLOPS under junction limit + eclipse + checkpoint) | first-principles thermal+compute coupling |
| `finance` | discounted cash flow (NPV/IRR), capital recovery, LCOE ($/PFLOP-hr), replenishment OPEX | standard project finance |
| `radiation` | cumulative TID vs shielding, shielding mass, SEU availability tax | SHIELDOSE-2/AE8-AP8, Suncatcher |
| `debris` | Poisson collision probability, fragmentation cascade | ORDEM 3.1 / MASTER-8, ESA SER 2025 |
| `propulsion` | drag make-up, Hohmann de-orbit, Δv budget, rocket equation | vis-viva, Tsiolkovsky |
| `reliability` | R(t), k-of-n redundancy, constellation availability, sparing | MIL-HDBK-217F, NASA SSRI |
| `compute` | delivered PFLOPS, MFU, radiation tax, effective PUE, $/PFLOP-hr | Google/NVIDIA, LBNL/Uptime |
| `economics` | per-sat cost, launch cross-over, CAPEX, 10-yr TCO | SpaceX, analyst |
| **`system`** | **integrated `DesignPoint` + `constellation` (budget closure)** | — |
| `montecarlo` | uncertainty propagation + one-at-a-time sensitivity | — |
| `figures` | publication figures with `DATA SOURCE` credit lines | — |

## Quick start

```bash
pip install -e ".[dev]"   # editable install with test deps (or: pip install -r requirements.txt)
python validate.py        # 23 worked-example checks (CI-style); exit 0 = all pass
pytest -q                 # 83-test suite: worked examples + property tests + integration
python run_study.py       # solves design point + constellation + Monte-Carlo, writes figures/
```

## What the integrated model does

`DesignPoint.solve()` runs the real engineering chain and returns a consistent design:

```
chips → compute power → power budget → solar-array area & mass → battery
      → thermal load → radiator area & mass → shielding mass
      → dry-mass rollup → ballistic coefficient → Δv budget → propellant
      → natural lifetime & disposal check → debris risk
      → delivered PFLOPS, effective PUE → per-satellite cost
```

`constellation()` aggregates to fleet PFLOPS / power / CAPEX / TCO and an availability estimate.
`montecarlo.monte_carlo()` propagates the solar-cycle, debris-flux, MFU, and chip-TDP
uncertainties to 5/50/95th-percentile outputs.

## Figures

`run_study.py` writes a figure set covering the **new** subsystems (the survivability figures
live in the companion repo): power (`fig_power`), optical link budget & pointing (`fig_comms`),
reliability & availability (`fig_reliability`), compute economics (`fig_compute`), the
integrated mass budget (`fig_mass_budget`), and Monte-Carlo uncertainty (`fig_montecarlo`).

## Accuracy and honesty

- **Validated:** `validate.py` ties 23 functions to worked examples, including an exact
  reproduction of the Part I thermal baseline (`thermal.report_i_baseline()`).
- **Sourced:** every input is in [docs/SOURCES.md](docs/SOURCES.md) with a confidence flag.
- **Honest caveats:** the TPU v6e TDP is undisclosed (treated as ~150–200 W); the solar-cycle
  density swing (~100×) dominates lifetime/Δv uncertainty and is shown as a band; these are
  first-order *sizing* models, not flight design.

## License & citation

MIT ([LICENSE](LICENSE)). Cite via [CITATION.cff](CITATION.cff). Independent corrections and
pull requests are welcome.
