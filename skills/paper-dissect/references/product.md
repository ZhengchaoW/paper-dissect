# The reader: what it shows and why

One self-contained HTML page, three panes, one graph.

## Source pane (left)

Every unit in order, grouped by section. The left stripe is the role colour of the unit's
node; dotted stripe = echo; italic = connective that became edge evidence; grey struck-through
with a reason = discard; grey without stripe = not yet dissected. Figures referenced in the
LaTeX source are embedded under their captions; tables are converted from `tabular`. Clicking
a unit selects its node; selecting a node scrolls here and highlights its spans. Nothing in the
paper is hidden from this pane — it is the denominator.

## Storyline pane (middle)

**Inquiry (default).** Columns by inquiry role: Research question → Refined into (design goals,
requirements, evaluation questions, each carrying "because: <problem>") → Answered by (claims
and the approach constructs) → Contribution → Open. Arrows are `refines` and `answered_by`,
plus relations derived through hidden evidence (dotted). Asides (interpretations, comparisons)
are hidden by default. Layout: column by role, rows by source order, answers kept next to the
target they answer.

**Narrative (toggle).** Columns by story function in the order the paper tells it: Problem →
Goal → Approach → Answers·theory → Evaluation → Answers·experiments → Contribution → Open.

**open ▸ on a claim → evidence graph.** The claim's direct warrants (proved, derived, observed
statements) plus one hop of setup behind each warrant (`uses`, `requires`, `qualifies`); other
story nodes appear as dashed "elsewhere" ports; proofs are never entered. This is the
warrant-boundary rule: a theorem's own prerequisites belong to the theorem's layer.

**open ▸ on a result → proof graph.** Prerequisites (assumptions, definitions, lemmas — dashed
ports, each lemma openable) → steps in chain order → the theorem. Layout by dependency
(longest path), which is the right axis inside a proof.

**open ▸ on a target → its answers** and the problems that motivated it.

Breadcrumb walks back up. Every graph is derived from the same node/edge data; lifting an
edge whose endpoint is hidden onto its visible ancestor keeps each level a quotient of the one
below.

**Score tab.** The same graph as rows in source order with arcs for relations. "by idea" folds
every node under its immediate post-dominator over dependency edges (steps → proof → theorem),
so a theorem's lemmas and a claim's private evidence collapse under it while shared setup stays
at section level. "by section" is the paper's own hierarchy. Fold levels: Sections / Ideas /
Steps.

## Focus pane (right)

The selected node: chip (warrant or subtype), function tag, statement, location, verbatim
spans and echoes, "Rests on" / "Feeds into" lineage, incoming and outgoing relations each with
their evidence sentence, "Open … graph ▸", and "What if this changes?" which tints every
downstream dependent (over dependency edges only) in whichever view is open.

## Layout rules worth keeping

- Top layer by *function*, proofs by *dependency*, score by *source order*. Never layer the
  storyline by topological depth: it scatters the story.
- Edges on the score are arcs (nodes on a line), so no edge ever crosses a node.
- Narrative relations (motivates, refines, answered_by) are excluded from what-if and from the
  cycle check.
- Coverage bars in the header are computed from the per-unit assignments, not from the graph.
