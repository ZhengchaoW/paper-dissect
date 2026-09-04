# Writing `dissection.py`

`dissection.py` is a plain Python file that builds a `Dissection` against `skeleton.json` and
calls `build()`. Keep it readable: one call per node, in source order, with a section comment
per section; relations at the end. It is the durable, diffable record of the dissection.

```python
import sys, os
sys.path.insert(0, "<skill dir>/scripts")
from dissect_lib import Dissection

skeleton, out = sys.argv[1], sys.argv[2]
D = Dissection(skeleton, title="Example Paper", dissected_through="s0440")
```

`dissected_through` is the last unit you fully partitioned; everything after it may stay
unassigned (it is reported, not hidden). Choose it at a section boundary.

## Spans

`D.sp("s0016", "s0018", ("s0020", "s0024"))` → a list of unit ids; tuples are inclusive ranges.
Every id must exist; a unit may be the home span of only one node.

## Nodes

```python
D.statement(id, label, text, warrant=..., function=..., spans=D.sp(...), echoes=D.sp(...), parent=None)
D.target(id, label, text, subtype=..., spans=..., echoes=...)                 # function derived from subtype
D.construct(id, label, text, subtype=..., function=..., spans=..., shape="atom"|"container", story=False)
D.proof(id, parent=<theorem id>, label=..., text=..., spans=D.sp("s0392"))    # spans = the "Proof." unit
D.step(id, parent=<proof id>, label="4 · …", text="", spans=...)
D.skeleton_env(<env label or id>, id, label, warrant="proved", function="guarantee", echoes=...)
D.undissected_proof(id, parent=<theorem id>, start="s0462", end="s0467", label="Proof of Lemma 4")
```

- `label`: ≤ 70 characters, a statement in the reader's language, not a topic ("Thm 2 = image→text
  translation with its own trainable drift", not "Theorem 2 discussion").
- `text`: the idea in one or two sentences; may be empty for steps whose label says it all.
- `parent`: only for non-section containment (steps → proof, proof → theorem, sub-methods →
  container construct). Section parents are assigned automatically from the home span.
- `echoes`: restatements elsewhere. `story=True` on a construct puts it on the storyline;
  `story=False` on a main-body claim keeps it off the storyline and folds it under the storyline
  claim it `supports` (it then appears in that claim's evidence graph as a sub-claim).
- `skeleton_env` takes the LaTeX `\label` (e.g. `"lem:projection"`) or the generated env id
  (`"lemma:4"`, see `skeleton.json → envs`) and uses the environment's units as the span.

## Relations and connectives

```python
D.edge(src, dst, type, ev=["s0124"], basis="explicit"|"inferred", note="…")
D.edge_evidence("s0124", src, dst)   # this unit's primary home is the relation (creates it if missing)
D.discard("pointer", "s0108", ("s0257", "s0259"))
```

Type vocabulary and direction are in `taxonomy.md`. Duplicate (src, dst, type) triples are
merged. Write the relations block after all nodes; it is easier to audit.

## Build

```python
report = D.build(out)        # raises DissectionError listing every problem when invalid
```

Writes `out/graph.json` (nodes, edges, per-unit assignments, sections, refs, macros, report)
and `out/coverage.md`. `report["problems"]` (fatal): unknown node/parent ids, duplicate ids,
overlapping spans, unassigned units in the dissected range, unknown labels, dependency cycles,
steps without a proof parent, targets with a non-target function. `report["warnings"]`:
targets without `answered_by`, claims without `supports`/`entails`/`develops`.

Typical fix loop: run → read the problem list → add the missing assignment (a node span, an
echo, an edge evidence, or a discard with a reason) → run again. Zero unassigned units in the
dissected range is the definition of done for the partition.

## Granularity guidance

Keep nodes small enough to express one assertable statement, construct, or target. Most nodes
should span one to six semantic units. Treat abstract, introduction, and conclusion summaries
as echoes when their warranted home appears elsewhere in the paper.
