# Equation provenance and cross-checks

Each governing equation in `orbital_dc` is listed with the primary reference it was checked
against, the status of that check, and any caveat. Confirmations come from an independent
literature cross-check against the named sources. Where a form could not be tied to a single
primary citation, it is marked as an estimate and stated as such in the code and the report.

## Astrodynamics (Curtis, *Orbital Mechanics for Engineering Students*, 1st ed., 2005)

| Quantity | Form | Reference | Status |
|---|---|---|---|
| Vis-viva / specific energy | v^2/2 - mu/r = -mu/2a | Curtis Ch 2, Eq 2.47 | confirmed verbatim |
| Circular speed | v = sqrt(mu/r) | Curtis Ch 2, Eq 2.53 | confirmed verbatim |
| Period (Kepler III) | T = 2 pi sqrt(a^3/mu) | Curtis Ch 2, Eq 2.73 | confirmed verbatim |
| J2 nodal precession | dOmega/dt = -(3/2) sqrt(mu) J2 R^2 cos i / [(1-e^2)^2 a^(7/2)] | Curtis Ch 4, Eq 4.47 | confirmed; SSO at ~98.4 deg |
| Hohmann delta-v | dv = dv_A + dv_B (tangential, from vis-viva) | Curtis Ch 6 | confirmed |
| Clohessy-Wiltshire | x'' - 3n^2 x - 2n y' = 0; y'' + 2n x' = 0; z'' + n^2 z = 0 | Curtis Ch 7, Eq 7.26 | confirmed verbatim |
| Rocket equation | dv = Isp g0 ln(m0/mf) | Curtis Ch 11, Eq 11.28 | confirmed verbatim |

## Thermal control (Gilmore *Spacecraft Thermal Control Handbook* 2nd ed.; NASA S3VI; Incropera)

| Quantity | Form | Reference | Status |
|---|---|---|---|
| Gray-body radiation | P = eps sigma A T^4 | NASA S3VI; Incropera; Gilmore Ch 2/15 | confirmed |
| Single-node energy balance | Q_net = q_IR A_IR + (1+a) q_sun A_sun s alpha + Q_gen - A_s sigma eps T^4 | NASA S3VI Eq 7 | confirmed |
| Lumped-capacitance transient | m c_p dT/dt = Q_in - Q_out | NASA S3VI Eq 8 | confirmed; add explicit Biot check (Bi = h Lc / k < 0.1, Incropera) for non-CubeSat scales |
| Earth IR (OLR) | q_IR ~ 231-258 W/m^2 (hot case), 237 used | Gilmore Ch 2 / NASA TM-2001-211221 | confirmed range |
| Albedo load | q = S0 a F alpha (a is reflectivity, not a flux; geometry/cosine factor applies) | Gilmore Ch 2 | confirmed; pitfall noted |
| Earth view factor | F = 0.5(1 - sqrt(1-(R_E/r)^2)) orientation-averaged; (R_E/r)^2 nadir flat plate | Modest, Radiative Heat Transfer | ESTIMATE: orientation-dependent; no single primary form for the averaged value, used as a representative estimate |

## Environment constants and models

| Item | Value used | Note |
|---|---|---|
| Solar constant | 1361 W/m^2 (modern TSIS-1/TIM) | textbook/Gilmore uses 1367 W/m^2 (older WRC). Modern value used here. |
| Stefan-Boltzmann | 5.670374e-8 W/m^2/K^4 | CODATA |
| Trapped radiation | AE8/AP8 (legacy), AE9/AP9 (newer) | both are authoritative; AE9/AP9 is the updated dataset |
| Dose-depth | SHIELDOSE-2 | standard engineering tool |
| SEU rate | R = sigma_SEU phi N_bits | simplified; the rigorous method integrates the measured cross-section curve over the spectrum (CREME96). Flagged as a first-order estimate. |
| Atmosphere | NRLMSIS 2.1 | density anchors |

## Power, optics, reliability, economics

| Quantity | Form | Reference | Status |
|---|---|---|---|
| Solar array output | P = S0 A eta(T,life) kappa eta_path | SMAD; Patel | confirmed; III-V multi-junction |
| Battery sizing | m = P_L t_e / (DoD e_sp) | SMAD; Patel | confirmed |
| Telescope gain | G = (pi D / lambda)^2 | FSO link-budget literature | confirmed (max on-axis, uniform aperture) |
| Free-space loss | L = (4 pi R / lambda)^2 | FSO link-budget literature | confirmed |
| Gaussian pointing loss | exp(-2 theta_err^2 / theta_div^2) | FSO references | confirmed |
| Reliability | R(t) = exp(-t/MTBF) | MIL-HDBK-217; reliability texts | confirmed |
| k-of-n redundancy | sum_{i=k}^n C(n,i) p^i (1-p)^(n-i) | standard reliability theory | confirmed |
| LCOE / CRF | (CRF*CAPEX + OPEX)/energy; CRF = r(1+r)^n/((1+r)^n-1) | NREL Simple LCOE | confirmed |

## Corrections applied
- Earth view factor: the code now documents that the value used is the orientation-averaged
  (spherical-body) factor and adds `earth_view_factor_nadir` for the flat-plate bound. The report
  states which is used and that the quantity is orientation-dependent, rather than asserting a
  single textbook form.
- Solar constant uses the modern 1361 W/m^2; the older 1367 W/m^2 is noted.
- The SEU model is labelled a first-order estimate; CREME96 is the rigorous method.
