# Space-Based Data Center Infrastructure: A Multi-Physics Approach

A complete, fully sourced, reproducible systems-engineering study of artificial-intelligence data
centers in low Earth orbit, together with the open Python models that produce every number and
figure, a derivation-by-derivation mathematical treatment, a typeset monograph, and a 3D
visualization. The reference architecture is Google's Project Suncatcher
([arXiv:2511.19468](https://arxiv.org/abs/2511.19468)).

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![tests](https://img.shields.io/badge/pytest-122_passing-success) ![subsystems](https://img.shields.io/badge/subsystems-20%2B-informational)

> **Summary.** Radiative cooling is the solved part of orbital AI compute, now flight-proven by
> Starcloud's H100. The open problems are orbital-debris survivability in a tight formation,
> mandatory active de-orbit, and launch economics. Engineering effort should follow the risk.

---

## Repository layout

| Folder | Contents |
|---|---|
| [`systems-model/`](systems-model) | `orbital_dc`, the full Python package across roughly twenty subsystems (orbit, thermal, power, attitude, communications, ground link, structures, radiation, debris, propulsion, reliability, compute, workload, finance, economics) with an integration layer that closes the mass, power, thermal, and Δv budgets, a Monte-Carlo module, a 122-test suite, and continuous integration. |
| [`survivability-model/`](survivability-model) | A focused survivability model (single module, twelve pure functions, a fourteen-check validation, seven figures). |
| [`report/`](report) | The complete study and the derivation-by-derivation mathematical guide (Markdown and HTML), all figures, and the figure-generating code. |
| [`book/`](book) | The typeset monograph as an Overleaf-ready LaTeX bundle (designed cover, full front matter, every chapter, all figures, equations, and code listings). |
| [`animation/`](animation) | A cinematic 3D visualization of the constellation, plus a caption-free copy. |

## Headline results (all reproduced by the code)

| Question | Result | Implication |
|---|---|---|
| Natural decay at 650 km | ~22 yr (4 yr at solar maximum, 312 yr at solar minimum) | Fails the FCC five-year rule; active de-orbit is mandatory |
| Does cooling scale? | ~1,500 m²/MW; the passive chip chain saturates above ~400 W | High-power accelerators need liquid cooling at the die |
| Debris risk per cluster over 5 yr | ~17% central (6–46% band) | The binding constraint, worsened by the tight formation |
| In-cluster cascade at 150 m | ~8.5% neighbour-hit per fragmentation | The formation paradox |
| Radiation | ~1 krad/5 yr behind 10 mm Al; ~10–20% upset throughput tax | Survivable, with a real and bounded cost |
| Controlled de-orbit | ~132 m/s, dominating the ~190 m/s Δv budget | Disposal is a primary mission function |
| Launch-cost parity at $200/kg | Reached in only a small minority of scenarios; median ~2044 where reached | Later and less certain than the headline date |

## Quick start

```bash
# the comprehensive systems model
cd systems-model
pip install -e ".[dev]"
python validate.py     # worked-example checks
pytest -q              # 122-test suite
python run_study.py    # full study and figures

# the focused survivability model
cd ../survivability-model
pip install -r requirements.txt
python survivability.py   # regenerate the figures
python validate.py        # validation checks
```

## Reproduce everything

```bash
pip install numpy matplotlib pytest
python reproduce_all.py   # runs both models' validation and tests, and regenerates every figure
```

See [`REPRODUCE.md`](REPRODUCE.md) for a step-by-step guide and how to verify any single number.

## Read the study

- **Monograph (recommended):** the Overleaf-ready LaTeX bundle in [`book/`](book)
  (`Space_Data_Center_Book_Overleaf.zip`); compile with the standard pdfLaTeX recipe.
- **Complete report:** [`report/Report_II_Complete.html`](report/Report_II_Complete.html), or the
  Microsoft Word version [`report/Report_II_Complete.docx`](report/Report_II_Complete.docx).
- **Mathematical guide (every derivation in full):** [`report/Mathematical_Guide_Complete.html`](report/Mathematical_Guide_Complete.html)
- **Cost-parity prediction (Monte-Carlo):** `python report/predictions.py`

The HTML files open in any browser; the mathematical guide typesets through the MathJax CDN on first
load.

## Visualization

Open [`animation/orbital_compute_premium.html`](animation/orbital_compute_premium.html) in a browser
(it fetches textures online). Keys: `1/2/3` hero poses, `S` save a frame, `H` toggle the HUD,
`Space` pause, `B` bloom, `F` satellite count.

## Accuracy and sources

Every input is sourced, with confidence flags, in each model's `docs/SOURCES.md`. The weakest single
input is the accelerator power, undisclosed by the vendor and treated as a 150-to-200-watt band; the
largest physical uncertainty is the roughly hundredfold solar-cycle density swing, carried as an
explicit band. These are first-order sizing and risk-ranking models, not flight design, and the text
keeps a strict line between demonstrated capability and projection.

## License and citation

Code is released under the MIT License ([LICENSE](LICENSE)); the report text and figures under
CC BY 4.0. Citation metadata is in [CITATION.cff](CITATION.cff). Independent reproduction and
corrections are welcome.
