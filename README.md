# Space-Based AI Data Centers — Open Models, Study, and Visualization

Everything behind the **"Space-Based AI Data Centers, Part II"** study: a complete, fully-sourced,
reproducible systems-engineering analysis of orbital AI compute, the open Python models that
produce every number and figure, a derivation-by-derivation mathematical guide, and a premium 3D
visualization. Reference architecture: Google **Project Suncatcher** ([arXiv:2511.19468](https://arxiv.org/abs/2511.19468)).

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![tests](https://img.shields.io/badge/pytest-108_passing-success) ![validation](https://img.shields.io/badge/validation-23_checks-success) ![subsystems](https://img.shields.io/badge/subsystems-17-informational)

> **Thesis:** radiative cooling is the *solved* part of orbital AI compute (now flight-proven by
> Starcloud's H100). The unsolved parts are orbital-debris survivability in a tight formation,
> mandatory active de-orbit, and economics. Effort should follow the risk.

---

## What's in here

| Folder | Contents |
|---|---|
| [`systems-model/`](systems-model) | **`orbital_dc`** — the full **17-subsystem** Python package (orbit, thermal, power, ADCS, comms, **ground link**, **structures**, radiation, debris, propulsion, reliability, compute, **workload/thermal-throttle**, **finance**, economics) + an integration layer that closes the mass/power/thermal/Δv budget, Monte-Carlo, **108-test pytest suite**, and CI. |
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

## Reproduce everything (one command)

```bash
pip install numpy matplotlib pytest
python reproduce_all.py      # runs both models' validation + tests + all figures + equation images
```

See [`REPRODUCE.md`](REPRODUCE.md) for a step-by-step guide and how to verify any single number.

## Equations for LinkedIn / slides

LinkedIn does not render LaTeX, and copying an HTML page does not carry the math. So every
governing equation is also provided as a ready-to-upload **image**:
[`report/equations/`](report/equations) (25 PNGs, see its `INDEX.md`). Insert these where each
equation appears in a post or article.

## Read the study

- **The complete treatise (~60-page book — all models, derivations, 18 tables, predictions):**
  [`report/Report_II_Complete.html`](report/Report_II_Complete.html) ← start here, or the
  **Microsoft Word version** [`report/Report_II_Complete.docx`](report/Report_II_Complete.docx)
  (403 native, editable Word equations; 14 figures; 18 tables). Regenerate with `python report/make_docx.py`.
- **Concise master report:** [`report/Master_Report.html`](report/Master_Report.html)
- **Mathematical guide (every derivation in full):** [`report/Mathematical_Guide_Complete.html`](report/Mathematical_Guide_Complete.html)
- **Cost-parity prediction (Monte-Carlo):** `python report/predictions.py`
- **LinkedIn-ready text + equation images:** [`linkedin/Master_Report_LinkedIn.txt`](linkedin/Master_Report_LinkedIn.txt), [`report/equations/`](report/equations)

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
