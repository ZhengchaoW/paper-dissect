"""paper-dissect DSL: author a per-paper dissection.py against a skeleton.json, validate it, export graph.json.

    from dissect_lib import Dissection
    D = Dissection("skeleton.json", title="Example Paper", dissected_through="s0440")
    D.statement("problem", "Problem — …", "…", warrant="interpreted", function="problem", spans=D.sp("s0016", "s0018"), echoes=D.sp("s0002"))
    D.target("question", "What should the method satisfy?", "…", subtype="research_question", spans=D.sp(("s0025", "s0028")))
    D.construct("method", "Proposed method", "…", subtype="model", function="approach", spans=D.sp(("s0029", "s0031")), story=True)
    D.proof("proof", parent="theorem", label="Proof of the main theorem", text="…", spans=D.sp("s0392"))
    D.step("proof_step", parent="proof", label="1 · …", text="", spans=D.sp("s0393", "s0394"))
    D.edge("theorem", "claim", "supports", ev=["s0036"])
    D.discard("signpost", "s0038"); D.discard("pointer", ("s0049", "s0050"))
    D.skeleton_env("lem:projection", "lem4", "Lemma 4 — …")            # statement from an undissected LaTeX environment
    D.undissected_proof("pf_lem4", parent="lem4", start="s0462", end="s0467", label="Proof of Lemma 4")
    report = D.build("out_dir")                                          # validates, writes graph.json + coverage.md

Every unit in s0001..dissected_through must end up as: a node span, an echo, edge evidence, a discard, or structure.
"""
import json, re, os, sys
from collections import Counter

KINDS = ("statement", "construct", "target", "proof", "step")
WARRANTS = ("cited", "assumed", "proved", "derived", "observed", "interpreted", "conjectured", "bounded")
TARGET_SUBTYPES = ("research_question", "desideratum", "design_goal", "evaluation_question", "open_question")
CONSTRUCT_SUBTYPES = ("definition", "construction", "representation", "method", "algorithm", "model", "dataset", "metric", "baseline")
FUNCTIONS = ("context", "problem", "motivation", "goal", "approach", "setup", "guarantee", "evaluation", "evidence", "theory_answer", "empirical_answer", "contribution", "interpretation", "comparison", "boundary", "future")
EDGE_TYPES = ("refines", "motivates", "answered_by", "requires", "uses", "entails", "supports", "proves", "qualifies", "challenges", "contrasts", "instantiates")
DEPENDENCY_TYPES = ("requires", "uses", "entails", "supports", "proves", "instantiates", "qualifies", "challenges", "contrasts")
DISCARD_REASONS = ("signpost", "pointer", "gloss", "illustration", "courtesy", "artifact", "declaration", "meta", "duplicate")
WARRANT_ROLE = {"cited": "background", "assumed": "assumption", "proved": "theorem", "derived": "derived", "observed": "experiment", "interpreted": "claim", "conjectured": "hypothesis", "bounded": "limitation"}
TARGET_FUNCTION = {"research_question": "goal", "desideratum": "goal", "design_goal": "goal", "evaluation_question": "evaluation", "open_question": "future"}


class DissectionError(Exception):
    pass


class Dissection:
    def __init__(self, skeleton_path, arxiv="", title="", dissected_through=None, source_id=""):
        self.sk = json.load(open(skeleton_path))
        self.S = {s["id"]: s for s in self.sk["sentences"]}
        self.ORDER = [s["id"] for s in self.sk["sentences"]]
        self.POS = {sid: i for i, sid in enumerate(self.ORDER)}
        self.meta = {"arxiv": arxiv, "title": title or self.sk.get("title", ""), "dissected_through": dissected_through or self.ORDER[-1], "source_id": source_id}
        self.nodes, self.edges, self.discards, self.edge_primary = {}, [], {}, {}
        self.env_by_id = {e["id"]: e for e in self.sk["envs"]}
        self.env_by_label = {e["label"]: e for e in self.sk["envs"] if e.get("label")}

    # ---------- spans ----------
    def rng(self, a, b=None):
        if b is None: return [a]
        i, j = self.POS[a], self.POS[b]
        if j < i: raise DissectionError(f"range reversed: {a}..{b}")
        return self.ORDER[i:j + 1]

    def sp(self, *parts):
        out = []
        for p in parts:
            out += self.rng(*p) if isinstance(p, tuple) else self.rng(p)
        for s in out:
            if s not in self.S: raise DissectionError(f"unknown unit {s}")
        return out

    # ---------- nodes ----------
    def _node(self, id, label, text, kind, sub, function, spans, echoes=(), parent=None, shape="atom", story=None, **kw):
        if id in self.nodes: raise DissectionError(f"duplicate node id {id}")
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", id): raise DissectionError(f"bad id {id}")
        if kind not in KINDS: raise DissectionError(f"{id}: bad kind {kind}")
        if function not in FUNCTIONS: raise DissectionError(f"{id}: bad function {function}")
        if not spans: raise DissectionError(f"{id}: a node needs at least one span")
        n = dict(id=id, label=label, text=text, kind=kind, sub=sub, function=function, spans=list(spans), echoes=list(echoes), parent=parent, shape=shape, **kw)
        n["role"] = {"statement": WARRANT_ROLE.get(sub), "target": "question", "construct": "definition" if sub in ("definition", "construction", "representation") else "method", "proof": "proof", "step": "step"}[kind]
        n["aside"] = function in ("interpretation", "comparison")
        n["story"] = bool(story) if story is not None else False
        self.nodes[id] = n
        return id

    def statement(self, id, label, text, warrant, function, spans, echoes=(), parent=None, story=None, **kw):
        if warrant not in WARRANTS: raise DissectionError(f"{id}: bad warrant {warrant}")
        return self._node(id, label, text, "statement", warrant, function, spans, echoes, parent, story=story, **kw)

    def target(self, id, label, text, subtype, spans, echoes=(), parent=None, function=None, **kw):
        if subtype not in TARGET_SUBTYPES: raise DissectionError(f"{id}: bad target subtype {subtype}")
        return self._node(id, label, text, "target", subtype, function or TARGET_FUNCTION[subtype], spans, echoes, parent, **kw)

    def construct(self, id, label, text, subtype, function, spans, echoes=(), parent=None, shape="atom", story=False, **kw):
        if subtype not in CONSTRUCT_SUBTYPES: raise DissectionError(f"{id}: bad construct subtype {subtype}")
        return self._node(id, label, text, "construct", subtype, function, spans, echoes, parent, shape=shape, story=story, **kw)

    def proof(self, id, parent, label, text, spans):
        return self._node(id, label, text, "proof", "proof", "guarantee", spans, (), parent, shape="container")

    def step(self, id, parent, label, text, spans):
        return self._node(id, label, text, "step", "step", "guarantee", spans, (), parent)

    def skeleton_env(self, env_key, id, label, warrant="proved", function="guarantee", echoes=()):
        e = self.env_by_label.get(env_key) or self.env_by_id.get(env_key)
        if not e: raise DissectionError(f"no environment {env_key}")
        ids = [f"s{k:04d}" for k in range(e["start"], e["end"] + 1)]
        return self.statement(id, label, "Statement taken verbatim from the LaTeX environment (skeleton only; not yet dissected).", warrant, function, ids, echoes, skeleton=True)

    def undissected_proof(self, id, parent, start, end, label):
        ids = self.rng(start, end)
        return self._node(id, label, "Not yet dissected — sentences shown as unassigned.", "proof", "proof", "guarantee", ids[:1], (), parent, shape="container", skeleton=True, undissected=ids[1:])

    # ---------- edges / discards ----------
    def edge(self, src, dst, type, ev=(), basis="explicit", note=""):
        if type not in EDGE_TYPES: raise DissectionError(f"bad edge type {type} ({src}->{dst})")
        if basis not in ("explicit", "inferred"): raise DissectionError(f"bad basis {basis}")
        self.edges.append(dict(id="", **{"from": src, "to": dst}, type=type, ev=list(ev), basis=basis, note=note))

    def edge_evidence(self, sid, src, dst):
        """Assign a connective sentence as the primary home of the edge src->dst (creates the edge if missing)."""
        self.edge_primary[sid] = (src, dst)

    def discard(self, reason, *ids):
        if reason not in DISCARD_REASONS: raise DissectionError(f"bad discard reason {reason}")
        for i in self.sp(*ids): self.discards[i] = reason

    # ---------- build ----------
    def build(self, out_dir, strict=True):
        S, ORDER, POS = self.S, self.ORDER, self.POS
        nodes, edges = self.nodes, self.edges
        problems = []
        for i, e in enumerate(edges): e["id"] = f"e{i + 1:03d}"
        # dedupe
        seen = set(); dd = []
        for e in edges:
            k = (e["from"], e["to"], e["type"])
            if k in seen: continue
            seen.add(k); dd.append(e)
        edges[:] = dd
        for i, e in enumerate(edges): e["id"] = f"e{i + 1:03d}"
        for e in edges:
            for end in ("from", "to"):
                if e[end] not in nodes: problems.append(f"edge {e['id']} {e['type']}: unknown node {e[end]}")
        for n in nodes.values():
            n["pos"] = min(POS[s] for s in n["spans"])
            if n["parent"] and n["parent"] not in nodes: problems.append(f"{n['id']}: unknown parent {n['parent']}")
        # story membership
        for n in nodes.values():
            if n["kind"] in ("statement", "target") and n["role"] in ("claim", "question") and not S[n["spans"][0]]["appendix"]: n["story"] = True
        # edge-evidence primaries
        primary = {}
        for sid, (a, b) in self.edge_primary.items():
            hit = next((e for e in edges if e["from"] == a and e["to"] == b), None)
            if hit is None: problems.append(f"edge evidence {sid}: no edge {a}->{b}"); continue
            if sid not in hit["ev"]: hit["ev"].append(sid)
            primary[sid] = hit["id"]
        # sections
        sections = []
        for s in self.sk.get("sections", []):
            sections.append(dict(s))
        if not sections or POS.get(sections[0]["start"], 0) > 0:
            sections.insert(0, {"id": "sec_abstract", "level": 0, "title": "Abstract", "start": ORDER[0], "appendix": False, "num": "", "label": ""})
        for i, sec in enumerate(sections):
            nxt = sections[i + 1]["start"] if i + 1 < len(sections) else None
            sec["end"] = ORDER[POS[nxt] - 1] if nxt else ORDER[-1]
            sec["pos"] = POS[sec["start"]]
        last = {0: None, 1: None}
        for sec in sections:
            lvl = sec["level"]
            sec["parent"] = None if lvl == 0 else (last[1] if lvl == 2 and last[1] else last[0])
            if lvl == 0: last[0] = sec["id"]; last[1] = None
            elif lvl == 1: last[1] = sec["id"]
        def section_of(sid):
            p = POS[sid]; best = None
            for sec in sections:
                if POS[sec["start"]] <= p <= POS[sec["end"]] and (best is None or sec["level"] >= best["level"]): best = sec
            return best["id"] if best else sections[0]["id"]
        for n in nodes.values():
            if n["parent"] is None: n["parent"] = section_of(n["spans"][0])
        # assignment table
        assign = {}
        def put(sid, rec, who):
            if sid in assign: problems.append(f"{sid} assigned twice: {assign[sid]} and {who}")
            else: assign[sid] = rec
        for n in nodes.values():
            for s in n["spans"]: put(s, {"kind": "node", "id": n["id"]}, n["id"])
            for s in n.get("undissected", []): put(s, {"kind": "undissected", "id": n["id"]}, n["id"])
        for sid, eid in primary.items(): put(sid, {"kind": "edge", "id": eid}, eid)
        for n in nodes.values():
            for s in n["echoes"]:
                if s not in assign: assign[s] = {"kind": "echo", "ids": [n["id"]]}
                elif assign[s]["kind"] == "echo": assign[s]["ids"].append(n["id"])
        for s, r in self.discards.items(): put(s, {"kind": "discard", "reason": r}, "discard")
        for s in self.sk["sentences"]:
            if s["kind"] in ("heading", "envhead") and s["id"] not in assign: assign[s["id"]] = {"kind": "structure"}
        limit = POS[self.meta["dissected_through"]]
        unassigned = [s for s in ORDER[:limit + 1] if s not in assign]
        for s in ORDER:
            if s not in assign: assign[s] = {"kind": "unassigned"}
        # semantic checks
        dep_adj = {}
        for e in edges:
            if e["type"] in DEPENDENCY_TYPES: dep_adj.setdefault(e["from"], []).append(e["to"])
        state = {}
        def dfs(u, stack):
            state[u] = 1; stack.append(u)
            for v in dep_adj.get(u, []):
                if state.get(v) == 1: problems.append("dependency cycle: " + " -> ".join(stack[stack.index(v):] + [v])); return True
                if state.get(v) is None and dfs(v, stack): return True
            stack.pop(); state[u] = 2; return False
        for u in list(nodes):
            if state.get(u) is None: dfs(u, [])
        warnings = []
        inE = {}; outE = {}
        for e in edges: inE.setdefault(e["to"], []).append(e); outE.setdefault(e["from"], []).append(e)
        for n in nodes.values():
            if n["kind"] == "target" and n["sub"] != "open_question" and not any(e["type"] == "answered_by" for e in outE.get(n["id"], [])):
                warnings.append(f"target {n['id']} has no answered_by edge")
            if n["role"] == "claim" and not n.get("skeleton") and not any(e["type"] in ("supports", "entails") for e in inE.get(n["id"], [])):
                warnings.append(f"claim {n['id']} has no supports/entails incoming edge")
            if n["kind"] == "target" and n["function"] not in ("goal", "evaluation", "future"): problems.append(f"{n['id']}: target with function {n['function']}")
            if n["kind"] == "step" and (not n["parent"] or nodes.get(n["parent"], {}).get("kind") != "proof"): problems.append(f"step {n['id']} must have a proof parent")
        if unassigned: problems.append(f"{len(unassigned)} unassigned units in the dissected range: {unassigned[:30]}")
        cov = Counter(a["kind"] for a in assign.values())
        by_role = Counter(nodes[a["id"]]["role"] for a in assign.values() if a["kind"] == "node")
        report = {"units": len(ORDER), "dissected_range": limit + 1, "coverage": dict(cov), "sentences_by_role": dict(by_role), "nodes": len(nodes), "edges": len(edges), "edge_types": dict(Counter(e["type"] for e in edges)), "inferred_edges": sum(1 for e in edges if e["basis"] == "inferred"), "problems": problems, "warnings": warnings}
        if problems and strict:
            raise DissectionError("dissection invalid:\n  " + "\n  ".join(problems))
        echo_of = {}
        for n in nodes.values():
            for s in n["echoes"]: echo_of.setdefault(s, []).append(n["id"])
        out = {"meta": self.meta, "refs": self.sk.get("refs", {}), "macros": self.sk.get("macros", {}),
               "sentences": [{**{k: v for k, v in s.items() if k in ("id", "kind", "text", "level", "env", "section", "appendix", "refs", "cites", "float", "labels", "graphics", "table_tex", "num")}, "assign": assign[s["id"]], "echo_of": echo_of.get(s["id"], [])} for s in self.sk["sentences"]],
               "sections": sections, "nodes": list(nodes.values()), "edges": edges, "report": report}
        os.makedirs(out_dir, exist_ok=True)
        json.dump(out, open(os.path.join(out_dir, "graph.json"), "w"), ensure_ascii=False)
        with open(os.path.join(out_dir, "coverage.md"), "w") as f:
            f.write(f"# Coverage — {self.meta.get('title') or self.meta.get('arxiv')}\n\n")
            f.write(f"Units: {len(ORDER)} · dissected range: s0001–{self.meta['dissected_through']} ({limit + 1} units)\n\n")
            f.write("| assignment | units |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in sorted(cov.items(), key=lambda kv: -kv[1])))
            f.write("\n| role | sentences |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in sorted(by_role.items(), key=lambda kv: -kv[1])))
            f.write(f"\nNodes: {len(nodes)} · edges: {len(edges)} ({report['inferred_edges']} inferred) · edge types: {report['edge_types']}\n")
            if warnings: f.write("\n## Warnings\n" + "".join(f"- {w}\n" for w in warnings))
            if problems: f.write("\n## Problems\n" + "".join(f"- {p}\n" for p in problems))
        return report
