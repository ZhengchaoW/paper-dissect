# Paper-dissect taxonomy

Three orthogonal axes per node. *Kind* says what sort of object a block is; *warrant* (for
statements) or *subtype* (for targets and constructs) says where its standing comes from;
*function* says what job it does in the paper's story. Display colour derives from kind and
warrant; function is only a tag. Never infer one axis from another and never encode a
function in an id prefix or a label.

## Kind

| kind | test | examples |
|---|---|---|
| **statement** | can be true or false; someone could assent to it | a claim, a theorem, an observation, an assumption, a cited fact, a limitation |
| **construct** | an object, not assertable; you define or build or run it | a definition, the base process, a training objective, an architecture, a dataset, a metric, an algorithm |
| **target** | a want, not assertable; things *answer* it | the research question, a criterion list, a design goal, "does it work on X?", future work |
| **proof** | container of the steps that establish one statement | Proof of Theorem 1 |
| **step** | one move inside a proof | "Pythagorean identity ⇒ f* is the unrestricted minimizer" |

Discourse (signposts, pointers, courtesies) is not a kind; it is discarded with a reason or
becomes edge evidence.

## Warrant (statements)

| warrant | meaning | role colour |
|---|---|---|
| cited | established elsewhere; the paper cites it | background |
| assumed | taken as given within a scope (mathematical assumption, modelling convention, evaluation condition) | assumption |
| proved | a formal result with a proof in the paper (theorem, lemma, corollary, proposition) | theorem |
| derived | derived in the text without a formal environment or proof (a closed-form density, a heuristic identity) | derived |
| observed | measured or seen in an experiment, table, figure, qualitative sample | experiment |
| interpreted | the authors' inference beyond what was proved or measured — every "claim" | claim |
| conjectured | stated as expected / hypothesised, to be tested | hypothesis |
| bounded | a statement about the limits of other statements (scope, caveat, failure mode) | limitation |

Test for interpreted vs. observed: could a second team with the same data write the sentence
without agreeing with the authors? "Flow matching fares worst on every metric" is observed;
"a deterministic ODE is unsuitable for this task" is interpreted.

## Target subtype

| subtype | what it is | where it sits in the inquiry tree |
|---|---|---|
| research_question | what the whole paper tries to answer; often a criteria list, rarely a question mark | root |
| desideratum | a requirement the solution must meet (a spec) | refinement |
| design_goal | a technical goal the construction must achieve ("a process with endpoint law p_data") | refinement |
| evaluation_question | a hypothesis in question form, attached to an experiment | refinement (evaluation) |
| open_question | left for future work | refinement with no answer |

## Construct subtype

definition · construction (a process, a measure, an objective) · representation (an encoding
of the data) · method (a procedure) · algorithm · model (an architecture or a named system) ·
dataset · metric · baseline.

## Story function

context · problem · motivation · goal · approach · setup · guarantee (theorems, proofs, steps)
· evaluation (evaluation questions) · evidence (experiments, observations) · theory_answer /
empirical_answer (claims that answer a target, by what warrants them) · contribution (the
paper's headline claims) · interpretation (an aside the authors draw) · comparison (vs. other
work) · boundary (limitations) · future.

Rules: a target's function is fixed by its subtype (goal / evaluation / future). A "problem" is
an interpreted (sometimes cited) statement about a deficiency; it `motivates` a target. The
storyline shows targets, answering claims/constructs and contributions; interpretations and
comparisons are asides, folded by default; context, setup, guarantees, evidence and boundaries
live one level down.

## Relations (source = earlier in the logic → target = what it enables/supports/motivates)

| type | from → to | use when |
|---|---|---|
| refines | target → target | a sub-goal, requirement or evaluation question of a broader target |
| motivates | problem / goal / claim → target or construct | the reason something is asked or built |
| answered_by | target → claim or construct | the thing that answers or satisfies the target |
| requires | assumption → statement / construct | a stated precondition |
| uses | construct → statement / construct / step; proved statement → step | invoked, applied, built upon |
| entails | statement → statement (incl. step → step) | logical consequence within the argument |
| supports | proved / derived / observed / cited → interpreted | evidence for a claim |
| proves | proof or terminal step → proved statement | |
| qualifies | bounded → statement | narrows scope or force |
| challenges | statement → statement | contradicts or weakens |
| contrasts | statement ↔ statement | positioned against |
| instantiates | statement → statement | a special case worked out |

`basis="explicit"` when the text states the relation; `"inferred"` when you added it. Attach
the connective sentence(s) as `ev`. Narrative types (refines, motivates, answered_by) may form
cycles with dependency types (hypothesis → test → evidence → hypothesis); dependency types
alone must be acyclic.

## Span assignments (per unit)

home · echo (restatement of a node whose home is elsewhere) · edge-evidence (a connective; the
primary home of a relation) · discard(reason) · structure (headings, environment labels).
Every unit up to `dissected_through` gets exactly one.

Home rule: the home of a claim is the statement nearest its warrant; abstract, introduction
summary and conclusion are echoes. A claim stated only in the intro/conclusion has its home
there — that is a fact about the paper and shows as a long arc.

## Discard reasons

signpost ("In this section we…"), pointer ("See Appendix B."), gloss (an intuition aside that
adds no claim), illustration (a rhetorical example), courtesy (acknowledgements), artifact
(LaTeX residue), declaration (AI-use / code-availability statements), duplicate.

## Inside proofs and experiments (optional finer labels)

Steps may be annotated in their label: setup · computation · invoke (a lemma) · case-split ·
conclude. A problem found in a proof is a `challenges` edge from a bounded statement to the
*step*, never a relabel of the theorem. Experiments may be split into setup, comparison,
observation and interpretation nodes when the sentences separate them.
