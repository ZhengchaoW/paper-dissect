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

**Inquiry (default).** Six columns defined by relations, never by a label: Why (problems, off by
default; each target carries "because: <problem>") → Root questions (targets nothing in the view
`refines`) → Refinements (targets with an incoming `refines`: goals, follow-up questions,
whatever their subtype) → Claims (statements with an incoming `answered_by`) → Synthesis
(claims reached only through `develops`) → Open. A node cannot qualify for both columns of a
pair, so the old "Research question / Refined into" and "Answered by / Contribution" overlaps
cannot recur. `contribution` is not a column and not a chip; a claim echoed in the abstract
shows "◆ abstract", which is derived from its echoes. Arrows are `refines`, `answered_by` and
`develops`; a relation between two nodes in the same column is drawn as a short down-arrow
(adjacent rows) or a rail beside the column, never a loop. A claim → question `motivates` hook
runs backwards in a column layout, so it is drawn only while that claim is selected. Rows: a
question and the claims that answer it share a row; a refinement starts on its parent's row;
each root starts a new block; a synthesis sits at the mean row of its sources. With "reduce" on,
a root's direct answer that is also reached through a refinement is not drawn (it stays in the
Focus pane).

**Narrative (toggle).** Columns by story function in the order the paper tells it: Problem →
Goal → Approach → Answers·theory → Evaluation → Answers·experiments → Contribution → Open.

**open ▸ on a claim → evidence graph.** Columns: Setup · elsewhere → Theory & experiments →
Sub-claims → Claim → Feeds into. From the claim, follow `supports` / `develops` / `entails`
backwards through interpreted statements that are *not* on the storyline (the sub-claims a
storyline claim folds, e.g. the per-stage claims under "three stages"), stop at warrants (proved,
derived, observed, bounded), then add one hop of setup behind each warrant (`uses`, `requires`,
`qualifies`). Other story nodes appear as dashed "elsewhere" ports; proofs are never entered.
Columns are ordered right-to-left so each warrant sits beside the sub-claim it supports. A claim
with no folded sub-claims has an empty Sub-claims column and its warrants attach directly. This
is the warrant-boundary rule: a theorem's own prerequisites belong to the theorem's layer.

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

Inline and display TeX render in both the Source and Focus panes. The renderer carries the
paper's extracted `\\newcommand`, `\\renewcommand`, `\\providecommand`, and `\\def`-family
macros into KaTeX, which is vendored with its fonts so the single HTML remains usable offline.

## Layout rules worth keeping

- Top layer by *relation-defined column* (roots / refinements / claims / synthesis), proofs by
  *dependency*, score by *source order*. Never layer the storyline by dependency depth (it
  scatters the story) and never by a label (it duplicates columns).
- Edges on the score are arcs (nodes on a line), so no edge ever crosses a node.
- Narrative relations (motivates, refines, answered_by, develops) are excluded from what-if and
  from the cycle check.
- Coverage bars in the header are computed from the per-unit assignments, not from the graph.
