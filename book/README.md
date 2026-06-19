# Space-Based AI Data Centers — the book

An Overleaf-ready LaTeX book built from the engineering study in
[`../report/Report_II_Complete.md`](../report/Report_II_Complete.md). It carries every
equation, derivation, table, and figure, in the house style of the
[samarjithbiswas.com](https://www.samarjithbiswas.com/books.html) handbook series
(IBM Plex Sans, teal palette, tcolorbox callouts).

## Compile

The fastest route is Overleaf (pdfLaTeX):

1. Download `Space_Data_Center_Book_Overleaf.zip`.
2. In Overleaf, **New Project → Upload Project**, select the zip.
3. Set the compiler to **pdfLaTeX** and compile `main.tex`.

Locally, with a full TeX Live install:

```
pdflatex main.tex && pdflatex main.tex   # twice for the table of contents
```

The build needs the `plex-sans`, `plex-mono`, `titlesec`, `tcolorbox`, and
`fontawesome5` packages, all present on Overleaf and in TeX Live.

## Regenerate

The book is a build target, not a hand-edited file. When the report changes,
regenerate it with:

```
pip install pypandoc-binary
python build_book.py
```

`build_book.py` preprocesses the Markdown (cover handling, part headings, currency,
tagged-equation conversion), runs pandoc as a standalone book, copies the figure
directories into the bundle, and writes both `main.tex` and the Overleaf zip.

## Files

- `main.tex` — the generated book (self-contained: the preamble and cover are inlined).
- `preamble.tex`, `cover.tex` — house style and cover page (inlined into `main.tex`).
- `build_book.py` — the generator.
- `figures/`, `figures2/`, `figures_pred/`, `systems_figs/` — figures used by the book.
