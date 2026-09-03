# Elucidating Flow Matching ODE Dynamics via Data Geometry and Denoisers

[Open the interactive reader](https://zhengchaow.github.io/paper-dissect/) ·
[PMLR paper](https://proceedings.mlr.press/v267/wan25e.html) ·
[arXiv source](https://arxiv.org/abs/2412.18730)

This is the worked example for Paper Dissect. It reconstructs the paper as an
inquiry-first graph:

1. the paper-level research questions;
2. claims that answer those questions;
3. theorem, experiment, assumption, definition, and method evidence behind each
   claim; and
4. ordered proof-step graphs behind the principal theorems.

The page keeps the complete 1,664-unit source visible. The main paper, through
unit `s0353`, is exhaustively partitioned. Selected appendix material expands
the principal proofs and every experiment section; the remaining appendix is
visible but explicitly marked not yet dissected.

## Included artifacts

- `dissection.py` — the paper-specific semantic decisions and typed relations;
- `graph.json` — the validated graph consumed by the reader; and
- `coverage.md` — the source-partition audit.

The hosted `docs/index.html` is generated from these artifacts and is fully
self-contained, including figures and KaTeX. Artifact labels and relations are
a first-pass AI dissection and have not been peer reviewed. The coverage audit
retains six warnings for author-framed problems or comparisons that intentionally
have no incoming evidence edge; they are not presented as experimentally
supported findings.

## Rebuild

From the repository root, after preparing arXiv `2412.18730` into `<workdir>`:

```sh
PAPER_DISSECT_SCRIPTS="$PWD/skills/paper-dissect/scripts" \
  python3 examples/elucidating-flow-matching/dissection.py \
  <workdir>/skeleton.json <workdir>/out

python3 skills/paper-dissect/scripts/render_html.py \
  <workdir>/out/graph.json docs/index.html --src-dir <workdir>/src
```
