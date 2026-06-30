# Report I — passive thermal feasibility (reproduction code)

This folder is the self-contained code for the first report, *Space-Based Data Center Infrastructure:
A Multi-Physics Approach (Part I)*, which asked whether a TPU-class compute node can reject its heat
passively in low Earth orbit and stay inside its junction-temperature budget.

## Run it

No third-party packages are required — only the Python standard library.

```bash
python report_one_thermal.py
```

The script prints the full analysis and finishes with a block of self-checks against the published
values. It exits `0` only if every check passes.

## What it reproduces

| # | Quantity | Result |
|---|----------|--------|
| 1 | Heat load (4 × 300 W TPU + avionics + parasitic) | 1450 W |
| 2 | Radiator temperature (Newton-Raphson on the Stefan-Boltzmann balance, 4 m², ε = 0.85) | 21.3 °C |
| 3 | Junction-to-radiator resistance chain (before / after optimization) | 0.350 / 0.300 K/W |
| 4 | Junction temperature and margin to the 125 °C limit | 111.3 °C, margin 13.7 °C |
| 5 | Single-heat-pipe-failure case (8 pipes → 7) | 114.8 °C |
| 6 | Passive thermal wall (max chip power within budget) | 346 W per chip |
| 7 | External loads (view factor, solar, albedo, Earth-infrared) | F = 0.290; 71 W albedo, 234 W IR |
| 8 | Eclipse transient (lumped capacitance, dawn-dusk grazing) | negligible (~0.5 °C) |

Every formula is written out in the source, with the iteration trace for the Newton-Raphson solve and
the component breakdown for the resistance chain, so the numbers can be followed by hand.

## Notes on the numbers

- The margin prints as 13.7 °C; the original report rounded it to 13.6 °C. Both come from the same
  T_j = 111.3 °C — it is a rounding difference, not a model change.
- The solar constant is taken as 1367 W/m² as in the original study. The modern TSIS-1 value is
  1361 W/m²; this changes the solar term by under one percent and no conclusion.
- The failure case is shown two ways: the published convention (scaling the 0.080 K/W nominal pipe
  value, giving 114.8 °C) and an alternative that scales the optimized 0.050 K/W pipe (113.5 °C). The
  conclusion — the node survives a single pipe loss with margin to spare — holds either way.

## Relationship to the rest of the repository

The same physics is implemented independently, with a full automated test suite, in
[`systems-model/orbital_dc/thermal.py`](../systems-model/orbital_dc/thermal.py) (see
`report_i_baseline()` there). That package extends the analysis to the other subsystems covered in the
later work. This folder is the standalone, dependency-free version meant to be read and run on its own.
