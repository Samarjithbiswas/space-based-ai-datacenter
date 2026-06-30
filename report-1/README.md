# Report I thermal code

Passive thermal sizing for the 1.45 kW TPU node at 650 km. Standard library only.

```bash
python report_one_thermal.py
```

Covers the heat budget, radiator temperature (Newton-Raphson on the Stefan-Boltzmann
balance), the junction-to-radiator resistance chain, junction temperature and margin,
the single-heat-pipe-out case, the maximum chip power inside the 125 C budget, the
solar/albedo/Earth-IR loads, and the eclipse transient. Key results: T_rad 21.3 C,
T_j 111.3 C (13.7 C margin), 114.8 C with one pipe out, passive wall 417 W per chip
(the interface rise alone reaches the 125 C budget, so no radiator size relaxes it).

Solar constant is 1367 W/m^2 as in the original study (modern value 1361, under 1%).
The same model is also in `systems-model/orbital_dc/thermal.py`.
