# Methods: Mathematical Foundation

Every model in `survivability.py` is first-order but derived from first principles. Each
section gives the governing physics, the derivation, the function that implements it, and a
worked example that `validate.py` checks.

## Constants

$\mu = 3.986004418\times10^{14}\ \mathrm{m^3 s^{-2}}$, $R_E = 6.371\times10^{6}\ \mathrm{m}$,
$\sigma = 5.670374\times10^{-8}\ \mathrm{W\,m^{-2}K^{-4}}$, $g_0 = 9.80665\ \mathrm{m\,s^{-2}}$,
$T_{\text{CMB}} = 2.725\ \mathrm{K}$.

## 1. Orbital preliminaries

Circular force balance $\mu m/a^2 = m v^2/a$ and $v=2\pi a/T$ give

$$v=\sqrt{\mu/a},\qquad T=2\pi\sqrt{a^3/\mu}.$$

At 650 km: $v=7534.8\ \mathrm{m/s}$, $T=97.6\ \mathrm{min}$. Specific energy $\mathcal{E}=-\mu/2a$.
→ `orbital_velocity`, `orbital_period`.

## 2. Atmospheric drag and orbital decay

Drag force $F_D=\tfrac12\rho v^2 C_D A$ → specific deceleration $a_D=\tfrac12\rho v^2 C_D (A/m)$.
Drag removes energy at $d\mathcal{E}/dt=-a_D v=-\tfrac12\rho C_D(A/m)v^3$. With
$\mathcal{E}=-\mu/2a\Rightarrow d\mathcal{E}/dt=(\mu/2a^2)\dot a$ and $v=\sqrt{\mu/a}$:

$$\boxed{\ \dot a=-C_D\,\frac{A}{m}\,\rho(h)\,\sqrt{\mu a}\ }$$

Integrated by adaptive forward Euler to re-entry at 120 km, with NRLMSIS 2.1 density (three
solar-activity scenarios; the ~100× min–max swing is the dominant uncertainty).
*Result:* 650 km, $A/m=0.0084$ → **~22 yr** (moderate), 4 yr (max), 312 yr (min).
→ `orbital_lifetime`.

## 3. Radiative balance and radiator sizing

Integrating Planck's law over a hemisphere and all wavelengths gives $E_b=\sigma T^4$. A gray
panel radiating to the CMB rejects $Q\approx\varepsilon\sigma A T^4$ (the $T_{\text{CMB}}^4/T^4\sim10^{-8}$
term is dropped). For a double-sided panel with parasitic fraction $f_p$:

$$\boxed{\ A_{\text{rad}}=\frac{Q}{\varepsilon\sigma T^4\,n_{\text{sides}}(1-f_p)}\ }$$

Linear in $Q$. *Worked:* 1 MW, 20 °C, $\varepsilon=0.90$ → $\varepsilon\sigma T^4=376.9\,\mathrm{W/m^2}$/side,
net $663.3\,\mathrm{W/m^2}$, $A=1508\,\mathrm{m^2}$. → `radiator_area`.

## 4. Conductive chain and interface saturation

Series resistances: $T_j=T_{\text{rad}}+Q\,R_{th}$. With $R_{th}=0.30\,$K/W the interface rise is
$\Delta T=P\times0.30$. Any chip with $P\,R_{th}>125\,$°C, i.e. $P>417\,$W, cannot be cooled
passively at any radiator size. → `junction_delta_T`.

## 5. Radiation dose vs shielding

$$\dot D(x)=D_0 e^{-x/\lambda}+D_\infty,\qquad \lambda\approx1.7\ \mathrm{mm},$$

calibrated to a $\sim$100–160 rad/yr proton floor (SIRI-1 600 km SSO; Suncatcher proton test).
*Worked:* 10 mm, 5 yr → **~1.06 krad(Si)** (under the ~2 krad HBM limit). → `tid_dose_rate`.

## 6. Debris impact probability (Poisson)

Rare independent impacts: from a binomial of $n$ slices each with $p=\Phi A\Delta t$, the
$n\to\infty$ limit gives a Poisson process with $\Lambda=\Phi A N t$, hence

$$\boxed{\ P(\ge1)=1-e^{-\Phi A N t}\ }$$

*Worked:* $\Phi=3\times10^{-5}$, $A=15$, $N=81$, $t=5$ → $\Lambda=0.182$, $P=16.7\%$.
→ `collision_probability`.

## 7. Fragmentation cascade coupling

$N_f$ lethal fragments spread over $4\pi d^2$; a neighbor of cross-section $\pi r_t^2$ intercepts
$\Lambda_n=N_f r_t^2/4d^2$, so

$$\boxed{\ P_{\text{hit}}(d)=1-\exp\!\Big(-\frac{N_f r_t^2}{4d^2}\Big)\ }$$

*Worked:* $N_f=2000$, $r_t=2\,$m, $d=150\,$m → $P_{\text{hit}}=8.5\%$. Since $P_{\text{hit}}\propto d^{-2}$,
1 km spacing drops it below 1 % but degrades the optical-link budget (the formation paradox).
→ `cascade_neighbor_probability`.

## 8. Δv: drag make-up, de-orbit, propellant

**Drag make-up:** $\Delta v=\int a_D\,dt=\tfrac12\rho v^2 C_D(A/m)t$ → ~13 m/s over 5 yr.
→ `drag_delta_v`.

**De-orbit (Hohmann):** transfer ellipse $a_t=(r_1+r_2)/2$; vis-viva gives
$v_{\text{apo}}=v_{c1}\sqrt{2r_2/(r_1+r_2)}$, so

$$\boxed{\ \Delta v_{\text{deorbit}}=v_{c1}\!\left(1-\sqrt{\frac{2r_2}{r_1+r_2}}\right)\ }$$

*Worked:* 650→180 km → **131.6 m/s**. → `deorbit_delta_v`.

**Propellant (Tsiolkovsky):** $m\,dv=-v_e\,dm$, $v_e=I_{sp}g_0$ →

$$\boxed{\ m_p=m_{\text{dry}}\!\left(e^{\Delta v/(I_{sp}g_0)}-1\right)\ }$$

*Worked:* $\Delta v=189.5\,$m/s, 375 kg → 34.4 kg (hydrazine) or 4.9 kg (electric).
→ `propellant_mass`.

## 9. Eclipse geometry

Critical beta angle below which eclipses occur: $\beta^\*=\arcsin\!\big(R_E/(R_E+h)\big)=65.1^\circ$
at 650 km, which is why a dawn-dusk SSO holds a >95 % illumination duty cycle.
→ `eclipse_critical_beta`.
