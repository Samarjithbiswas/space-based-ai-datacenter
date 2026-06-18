# Space-Based AI Data Centers — Open Models, Study, and Visualization

Everything behind the **"Space-Based AI Data Centers, Part II"** study: a complete, fully-sourced,
reproducible systems-engineering analysis of orbital AI compute, the open Python models that
produce every number and figure, a derivation-by-derivation mathematical guide, and a premium 3D
visualization. Reference architecture: Google **Project Suncatcher** ([arXiv:2511.19468](https://arxiv.org/abs/2511.19468)).

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![tests](https://img.shields.io/badge/pytest-83_passing-success) ![validation](https://img.shields.io/badge/validation-37_checks-success) ![subsystems](https://img.shields.io/badge/subsystems-13-informational)

> **Thesis:** radiative cooling is the *solved* part of orbital AI compute (now flight-proven by
> Starcloud's H100). The unsolved parts are orbital-debris survivability in a tight formation,
> mandatory active de-orbit, and economics. Effort should follow the risk.

---

## What's in here

| Folder | Contents |
|---|---|
| [`systems-model/`](systems-model) | **`orbital_dc`** — the full 13-subsystem Python package (orbit, thermal, power, ADCS, comms, radiation, debris, propulsion, reliability, compute, economics) + an integration layer that closes the mass/power/thermal/Δv budget, Monte-Carlo, **83-test pytest suite**, and CI. |
| [`survivability-model/`](survivability-model) | Focused survivability model (single module, 12 pure functions, 14-check validation, 7 figures). |
| [`report/`](report) | The complete Part II report and the **derivation-by-derivation mathematical guide** (Markdown + MathJax HTML), all figures, the figure-generating script, and an independent peer review of a related repo. |
| [`animation/`](animation) | A **premium cinematic 3D visualization** (photoreal day/night Earth, atmosphere, constellation, bloom) and a caption-free documentary copy. |
| [`linkedin/`](linkedin) | Copy-paste-ready article text. |

## Headline results (all reproduced by the code)

| Question | Result | Implication |
|---|---|---|
| 650 km natural decay? | ~22 yr (4 yr solar-max, 312 yr solar-min) | Fails the **FCC 5-yr rule** → active de-orbit mandatory |
| Does cooling scale? | ~1,500 m²/MW; passive chip chain saturates **>400 W** | H100/Blackwell need liquid cooling at the die |
| Debris risk / cluster / 5 yr | **~17%** central (6–46% band) | The binding constraint; worsened by the tight formation |
| In-cluster cascade @150 m | ~8.5% neighbor-hit per fragmentation | The "formation paradox" |
| Radiation | ~1.06 krad/5 yr behind 10 mm Al; ~10–20% SEU throughput tax | Survivable, but a real tax |
| De-orbit cost | ~132 m/s (dominates ~190 m/s Δv); ~5 kg electric prop | Permanent-vs-disposable penalty |
| Launch cost decisive? | No — below ~$600/kg, hardware dominates | Gated by hardware, lifetime, utilization |

## Quick start

```bash
# the comprehensive systems model
cd systems-model
pip install -e ".[dev]"
python validate.py     # worked-example checks
pytest -q              # 83-test suite
python run_study.py    # full study + figures

# the focused survivability model
cd ../survivability-model
pip install -r requirements.txt
python survivability.py   # regenerate the 7 figures
python validate.py        # 14 checks
```

## Read the study

- **Report (HTML, figures embedded):** [`report/Report_II_Complete.html`](report/Report_II_Complete.html)
- **Mathematical guide (every derivation, MathJax):** [`report/Mathematical_Guide_Complete.html`](report/Mathematical_Guide_Complete.html)

Open either in a browser; print to PDF if you want a document. The math guide needs internet on
first load to typeset (MathJax CDN).

## View the visualization

Open [`animation/orbital_compute_premium.html`](animation/orbital_compute_premium.html) in a
browser (needs internet for textures). Keys: `1/2/3` hero poses, `S` save PNG, `H` HUD,
`Space` pause, `B` bloom, `F` satellite count.

## Accuracy and honesty

Every input is sourced (see each model's `docs/SOURCES.md`) with confidence flags. The single
weakest input is the TPU v6e TDP (undisclosed by Google; treated as ~150–200 W). The largest
physical uncertainty is the ~100× solar-cycle density swing, shown as a band. These are
first-order *sizing* models, not flight design.

## License & citation

Code: **MIT** ([LICENSE](LICENSE)). Report text and figures: CC BY 4.0. Cite via
[CITATION.cff](CITATION.cff). Independent reproduction and corrections are welcome.

## Acknowledgements

This work exists because readers of Part I pushed back on the survivability and reproducibility
gaps. That feedback shaped the entire study.
