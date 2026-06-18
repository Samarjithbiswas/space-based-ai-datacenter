# Data Sources and Confidence

Every model input, with its value, source, and a confidence flag:
**[Official]** operator/agency primary doc · **[Model]** standard physics model ·
**[Estimate]** analyst/derived/secondary.

## Reference architecture (Project Suncatcher, arXiv:2511.19468) — all [Official]

| Parameter | Value | Notes |
|---|---|---|
| Orbit | dawn-dusk sun-synchronous, 650 km | confirmed in paper |
| Cluster | 81 satellites, 1 km radius lattice | square lattice |
| Inter-satellite spacing | 100–200 m (next-nearest) | drives optical link + cascade risk |
| Optical link | 800 Gbps one-way / 1.6 Tbps two-way @ 1.55 µm | bench demo; 9.6 Tbps theoretical |
| Accelerator | TPU v6e, 918 TFLOPS BF16, 32 GB HBM | per-chip power **not stated** |
| Radiation test | 67 MeV proton beam, UC Davis | 5-yr req **750 rad(Si)**; HBM limit ~**2 krad** |
| Expected LEO dose | ~150 rad(Si)/yr | |
| Launch viability | <$200/kg by ~2035 ($300/kg conservative) | |

## Hardware power (TDP)

| Chip | TDP | Flag | Source |
|---|---|---|---|
| TPU v6e | ~150–200 W (Google undisclosed) | **[Estimate]** | The Next Platform; Google Cloud docs |
| TPU v4 | 170 W measured / 250 W nameplate | **[Official]** | Google TPU v4 paper (arXiv:2304.01433) |
| NVIDIA H100 SXM | 700 W | **[Official]** | NVIDIA H100 datasheet |
| NVIDIA B200 | 1000 W (standalone) | **[Official]** | NVIDIA / ServeTheHome |
| NVIDIA GB200 GPU | 1200 W per GPU (2700 W superchip) | **[Official]** | ServeTheHome |
| GB200 NVL72 rack | ~120 kW | **[Confirmed]** | HPE / ServeTheHome |
| Starcloud-1 | flew **1× H100** in orbit, Nov 2025 | **[Confirmed]** | NVIDIA blog; DataCenterDynamics |

## Environment models

| Quantity | Value | Flag | Source |
|---|---|---|---|
| Atmospheric density @650 km | 1.6e-13 kg/m³ (moderate); ~100× solar-cycle swing | **[Model]** | NRLMSIS 2.1 (Picone et al. 2002) |
| Debris flux >1 cm @ SSO | 1e-5 – 1e-4 /m²/yr | **[Model]** | NASA ORDEM 3.1 / ESA MASTER-8 (NTRS 20210011563) |
| Debris flux >1 mm @ SSO | 1e-3 – 1e-2 /m²/yr | **[Model]** | ORDEM/MASTER |
| Tracked population (2025) | 54k >10 cm; 1.2M 1–10 cm; 130M 1mm–1cm | **[Official]** | ESA Space Environment Report 2025 |
| TID dose-depth | ~tens of krad/yr @1 mm → ~100–150 rad/yr floor | **[Model]** | SHIELDOSE-2 / AE8-AP8; SIRI-1 600 km SSO |
| Starlink avoidance maneuvers | 144,404 in H1 2025 (threshold lowered — partly reporting) | **[Official]** | SpaceX FCC filing |

## Thermal references

| Quantity | Value | Source |
|---|---|---|
| Stefan-Boltzmann constant | 5.670374e-8 W/m²/K⁴ | CODATA |
| CMB sink temperature | 2.725 K | Fixsen 2009 (COBE/FIRAS) |
| Z-93 / AZ-93 coating (BOL) | ε ≈ 0.92, α_s ≈ 0.15 | NASA NTRS |
| Z-93 / AZ-93 (EOL, conservative) | α_s → ~0.36, ε ~0.90 | NASA NTRS 19920048673 |
| ISS EATCS | 70 kW total, ~156 m² radiators, ammonia loops | NASA ATCS overview |
| Industry radiator rule | ~1,200 m²/MW @20 °C | "physics wall" landscape analyses |

## Launch economics

| Quantity | Value | Flag | Source |
|---|---|---|---|
| Falcon 9 list price | $69.75M; 18,500 kg reusable → **~$3,770/kg** | **[Official]** | SpaceX |
| Falcon 9 internal marginal | ~$1,500/kg (not customer price) | **[Estimate]** | analyst |
| Starship target band | $30 (aspirational) – $600/kg (realistic) | **[Estimate]** | analyst + Musk statements |
| Space Shuttle | ~$54,500/kg (program-averaged) | **[Estimate]** | widely cited |

## Regulatory

| Item | Value | Source |
|---|---|---|
| US LEO disposal rule | **5 years** (adopted 2022, effective Sept 2024) | FCC Second Report and Order 22-74 |
| International baseline | 25 years | IADC / ISO 24113 / NASA ODMSP |

---

### Honest caveats
- **TPU v6e TDP** is the weakest input (undisclosed). Treated as a ~150–200 W estimate.
- **Solar-cycle density swing (~100×)** dominates decay/drag uncertainty; shown as a band.
- **Debris flux** in the 1 mm–1 cm range is the least model-validated; ORDEM and MASTER can
  differ by 1–2 orders of magnitude there.
- These are sizing models, not flight design. For mission work use NASA DAS, ORDEM/MASTER,
  SPENVIS/SHIELDOSE-2, and a full thermal/orbit toolchain.
