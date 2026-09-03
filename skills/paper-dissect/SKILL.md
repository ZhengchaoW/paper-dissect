---
name: paper-dissect
description: Turn one research paper (arXiv id, LaTeX source, or PDF) into a self-contained interactive website backed by a bottom-up sentence partition and typed idea graph, including an inquiry-tree storyline, claim-to-evidence views, and theorem-to-proof views. Use when the user asks to dissect a paper, build its paper graph or storyline, show what questions it answers, inspect its claims and evidence, or render a paper as an interactive web page.
---

# Paper Dissect

Turn one paper into one self-contained interactive HTML reader by reconstructing the graph
of ideas that the paper linearised into text. The construction is
**bottom-up** (every sentence is partitioned, nothing is silently omitted); the reading is
**top-down** (research question → refinements → answers → contributions, then drill into a
claim's evidence and a theorem's proof). Each level is a quotient of the level below, so the
storyline can never say something the sentences do not support.

Codex performs the semantic step by writing `dissection.py`; the deterministic Python
pipeline uses only the standard library and the renderer embeds its vendored KaTeX runtime.

## Read first

- `references/taxonomy.md` — the labels (kinds, warrants, target/construct subtypes, story
  functions, edge types, span assignments, discard reasons) and the decision tests. Read it
  completely before labelling anything.
- `references/dsl.md` — the `dissection.py` API and the validation errors.
- `references/product.md` — what the reader shows and the layout rules it relies on.

## Pipeline

```sh
S=<this skill dir>/scripts
python3 $S/prepare.py <arxiv-id | latex-dir | paper.pdf> <workdir>   # fetch → flatten → segment; writes listing.txt
# read <workdir>/listing.txt from the top, write <workdir>/dissection.py (the model's job, see below)
python3 <workdir>/dissection.py <workdir>/skeleton.json <workdir>/out   # validates, writes graph.json + coverage.md
python3 $S/render_html.py <workdir>/out/graph.json <workdir>/out/index.html --src-dir <workdir>/src
```

`prepare.py` prefers the arXiv LaTeX source: theorem environments, labels, `\ref`s, equations,
figures and tables come out of it deterministically and become the skeleton. With a PDF only it
falls back to `pdftotext` (no environments, no figures; say so in the deliverable).

Use any task-appropriate work directory, such as `./paper-dissect/<paper-id>/`.

## The dissection pass (what the model does)

Read `listing.txt` in order, all of it. The unit ids (`s0001…`) are the coordinates of
everything you write. Then author `dissection.py` so that **every unit up to
`dissected_through` has exactly one primary assignment**:

1. **Node span** — the unit states (part of) an idea. One node = one assertable statement, one
   construct, or one target; typically 1–6 units, never a whole section. Restatements of the
   same idea elsewhere (abstract, intro summary, conclusion, a theorem previewed in prose) are
   **echoes** of the one node whose *home* is the statement nearest its warrant.
2. **Edge evidence** — the unit is a connective ("Therefore…", "This is Thm. 1's dual",
   "Consistent with Theorem 3, …"). It belongs to a relation, not a node:
   `D.edge_evidence(sid, src, dst)`.
3. **Discard with a reason** — signpost, pointer ("see Appendix B"), gloss, illustration,
   courtesy, artifact, declaration. Nothing is dropped without a label.
4. Headings and environment labels are structure and need no assignment.

Label every node on three axes (see the taxonomy): **kind** (statement / construct / target /
proof / step), **warrant or subtype** (cited, assumed, proved, derived, observed, interpreted,
conjectured, bounded; research_question, desideratum, design_goal, evaluation_question,
open_question; definition, construction, representation, method, algorithm, model, dataset,
metric, baseline) and **story function** (context, problem, motivation, goal, approach, setup,
guarantee, evaluation, evidence, theory_answer, empirical_answer, contribution,
interpretation, comparison, boundary, future). A "problem" is a function of an interpreted
statement, never a kind; it *motivates* a target and is displayed as that target's "because".

Relations are typed by what the source is: `requires` (assumption →), `uses` (construct →;
lemma → proof step), `entails` (statement → statement), `supports` (evidence → claim),
`proves` (proof/step → theorem), `qualifies` / `challenges` (limitation, counter-evidence →),
`contrasts`, `instantiates`, and the narrative trio `motivates`, `refines` (target → target),
`answered_by` (target → claim or construct). Mark `basis="inferred"` whenever the authors did
not state the relation; attach the connective sentence as `ev`.

Build the **question chain explicitly**: the research question (usually the paper's
criteria or "we want a model that…" list, even if never phrased as a question) `refines` into
design goals, requirements and evaluation questions; each of those is `answered_by` something;
open questions are `refines` children of the research question with no answer. If a target has
no `answered_by`, either you missed it or the paper leaves it open — decide which.

Hierarchy: a theorem's proof is `D.proof(...)` with `D.step(...)` children in order; steps
`entails` the next step and `uses` the lemmas/definitions they invoke. Sub-methods live under
a container construct (`shape="container"`). Dissect, at minimum: the whole main body, and the
proofs of the main theorems; register the remaining appendix environments with
`D.skeleton_env` / `D.undissected_proof` so the coverage ledger shows them honestly.

Mark the two or three constructs that *are* the approach with `story=True` so they appear on
the storyline; mark interpretations and comparisons with those functions so they fold as asides.

## Validate and review

`D.build()` fails on: unknown ids, overlapping spans, unassigned units in the dissected range,
bad labels, dependency cycles, steps outside proofs, targets with impossible functions. It warns
on targets with no answer and claims with no support. Fix errors; justify or fix warnings.

Then review your own graph against these questions before rendering:
- Does the inquiry tree read as the paper's argument? (research question → refinements →
  answers → contributions; nothing else in the top layer)
- Is anything labelled `problem` actually the negation of a criterion? If so, attach it to that
  criterion via `motivates`, don't make a second story node for it.
- Does each `interpreted` statement have a warrant (`supports`/`entails` incoming) or a visible
  reason it doesn't?
- Are theorems' statements separate from their proofs' status? (a proof `proves` a theorem; an
  issue inside a proof is a step-level challenge, not a relabel of the theorem)
- Are homes at the warrant and abstract/intro/conclusion restatements echoes?
- Is every `inferred` edge really absent from the text?
- Do representative inline and display equations render in both Source and Focus, including
  `\\(...\\)` / `\\[...\\]` delimiters and paper-defined macros such as `\\def` and
  argument-taking `\\newcommand`s?
- Does the generated HTML contain no external runtime dependency?

## Render and deliver

`render_html.py` produces one self-contained page: source pane (every unit, coloured by the
role of its node, connectives in italics, discards greyed with their reason, figures and
tables inline), Storyline pane (inquiry tree; `open ▸` on a claim → its evidence graph, on a
result → its proof graph; Narrative order as an alternative; the Score tab shows the same graph
in source order, folded "by idea"), Focus pane (verbatim spans, incoming/outgoing relations
with their evidence sentences, lineage, what-if). Source and Focus render inline/display TeX
and the paper's extracted macros. Use the default renderer to produce the portable offline
website.

Deliver: `index.html`, `graph.json`, `coverage.md`, `dissection.py`, and a three-line summary
with the coverage numbers (units, dissected range, nodes, relations, inferred relations,
undissected remainder) and what you left undissected. State that the labels are one pass and
unreviewed.

## Don'ts

- Don't select the "important" sentences first and skip the rest: partition, then label.
- Don't use one edge type for everything; `enables` is not in the vocabulary on purpose.
- Don't layer the storyline by dependency depth; the top layer is laid out by function.
- Don't paraphrase a theorem into its claim; the theorem stays a `proved` statement, the claim
  it answers is a separate `interpreted` statement `supports`-ed by it.
- Don't invent motivation edges from a problem to every target; one problem usually
  motivates one criterion.
