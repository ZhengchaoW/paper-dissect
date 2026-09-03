# Paper Dissect

Give Codex an arXiv ID, a LaTeX project, or a PDF. Paper Dissect turns that
single paper into a self-contained interactive website.

The generated page keeps the source text, the reconstructed argument, and the
supporting evidence together:

- every source unit is assigned, echoed, structurally labeled, or explicitly
  left outside the completed coverage boundary;
- the storyline runs from research questions to answers and contributions;
- claims open into evidence graphs and theorems open into proof steps; and
- the result is one portable offline `index.html` file with no web service or database.

## Install for Codex

Copy `skills/paper-dissect/` into your Codex skills directory, or point Codex
at [its `SKILL.md`](skills/paper-dissect/SKILL.md).

Then ask:

> Use `$paper-dissect` to turn this paper into an interactive website.

## Inputs and outputs

Accepted inputs:

- an arXiv identifier;
- a local LaTeX source directory; or
- a local PDF.

Each run produces:

- `index.html` — the self-contained interactive website;
- `graph.json` — the typed idea graph;
- `coverage.md` — the source-partition audit; and
- `dissection.py` — the paper-specific semantic mapping written by Codex.

The deterministic preparation and rendering code uses Python's standard
library and embeds the vendored KaTeX runtime in each page. PDF-only input additionally
requires `pdftotext`. LaTeX source gives
the best result because theorem environments, equations, references, figures,
and tables remain structurally available.

## Repository contents

This repository intentionally contains only:

- the installable Codex skill and its Python pipeline;
- the taxonomy, DSL, and reader references required by the skill;
- the MIT license.

Generated paper websites and downloaded paper sources belong in the user's
chosen work directory, not in this repository.
