#!/usr/bin/env python3
"""Segment a flattened LaTeX body into sentence-level units with structure.

Usage: parse_tex.py <flat.tex> <out_skeleton.json> [--listing out.txt]

Produces skeleton.json:
  sentences: ordered units {id, kind: heading|envhead|caption|math|sentence, text, section, section_label,
             env (enclosing theorem-like env id), appendix, refs, cites, [level], [labels], [float, graphics, table_tex]}
  envs:      theorem-like environments {env, id, title, label, start, end, number}
  refs:      label -> display string ("Thm. 1", "Eq. (7)", "§3.2", "Fig. 2", "App. A")
  sections:  heading units with numbering
The optional listing prints "s0123  text" lines for reading the paper in units.
"""
import re, json, sys, os

THM_ENVS = ["theorem", "lemma", "corollary", "proposition", "assumption", "remark", "definition", "conjecture", "claim", "example", "proof"]
FLOAT_ENVS = ["figure", "figure*", "wrapfigure", "table", "table*", "wraptable", "algorithm", "algorithm*", "sidewaysfigure", "sidewaystable"]
ABBR = ["e.g.", "i.e.", "et al.", "vs.", "Thm.", "Thms.", "Eq.", "Eqs.", "Fig.", "Figs.", "Sec.", "Secs.", "App.", "resp.", "cf.", "Prop.", "Def.", "Lem.", "Cor.", "approx.", "w.r.t.", "a.k.a.", "No.", "Alg.", "Tab.", "Ch.", "Dr.", "Mr.", "Ms.", "St.", "viz.", "etc."]

def read_braced(s, start):
    depth = 1; j = start
    while j < len(s) and depth:
        if s[j] == "\\": j += 2; continue
        if s[j] == "{": depth += 1
        elif s[j] == "}": depth -= 1
        j += 1
    return s[start:j - 1], j

def extract_floats(text):
    """Replace float environments by \\FLOAT markers carrying caption, labels, graphics and tabular source."""
    env_re = re.compile(r"\\begin\{(" + "|".join(re.escape(e) for e in FLOAT_ENVS) + r")\}")
    pos = 0; res = []
    while True:
        m = env_re.search(text, pos)
        if not m: res.append(text[pos:]); break
        name = m.group(1)
        pat = re.compile(r"\\(begin|end)\{" + re.escape(name) + r"\}")
        depth = 0; end = None
        for mm in pat.finditer(text, m.start()):
            depth += 1 if mm.group(1) == "begin" else -1
            if depth == 0: end = mm.end(); break
        if end is None: res.append(text[pos:]); break
        block = text[m.start():end]
        caps = []
        for cm in re.finditer(r"\\caption\*?(?:\[[^\]]*\])?\{", block):
            cap, _ = read_braced(block, cm.end()); caps.append(cap)
        labs = re.findall(r"\\label\{([^}]+)\}", block)
        gfx = re.findall(r"\\includegraphics\*?(?:\[[^\]]*\])?\{([^}]+)\}", block)
        tabs = re.findall(r"\\begin\{tabular[x*]?\}.*?\\end\{tabular[x*]?\}", block, flags=re.S)
        kind = "algorithm" if name.startswith("algorithm") else ("table" if "tab" in name else "figure")
        payload = json.dumps({"kind": kind, "labels": labs, "graphics": gfx, "table_tex": tabs[:2], "captions": caps})
        res.append(text[pos:m.start()] + "\n\\FLOAT" + payload + "\\ENDFLOAT\n")
        pos = end
    return "".join(res)

def parse(src, macros=None):
    text = extract_floats(src)
    elements = []; buf = []
    def flush():
        t = "".join(buf).strip()
        if t: elements.append({"type": "text", "text": t})
        buf.clear()
    tok = re.compile(
        r"(?P<sec>\\(?:sub)?(?:sub)?section\*?\{)|(?P<par>\\paragraph\*?\{)|(?P<app>\\appendix)|"
        r"(?P<envb>\\begin\{(?P<envname>" + "|".join(THM_ENVS) + r")\*?\}(?:\[(?P<envtitle>[^\]]*)\])?)|"
        r"(?P<enve>\\end\{(?P<envename>" + "|".join(THM_ENVS) + r")\*?\})|"
        r"(?P<float>\\FLOAT(?P<fpayload>\{.*?\})\\ENDFLOAT)|"
        r"(?P<dmb>\\begin\{(?P<dmname>equation\*?|align\*?|gather\*?|multline\*?|eqnarray\*?|flalign\*?|alignat\*?)\}|\\\[)|"
        r"(?P<input>%%(?:BEGIN|END)INPUT [^\n]*|%%MISSING [^\n]*)", flags=re.S)
    pos = 0
    while True:
        m = tok.search(text, pos)
        if not m: buf.append(text[pos:]); break
        buf.append(text[pos:m.start()])
        if m.group("sec"):
            flush(); title, j = read_braced(text, m.end()); level = m.group("sec").count("sub")
            lm = re.match(r"\s*\\label\{([^}]+)\}", text[j:]); label = lm.group(1) if lm else ""
            if lm: j += lm.end()
            elements.append({"type": "heading", "level": level, "title": title, "label": label, "starred": "*" in m.group("sec")}); pos = j
        elif m.group("par"):
            flush(); title, j = read_braced(text, m.end())
            elements.append({"type": "text", "text": title.rstrip(". ") + ":"}); pos = j
        elif m.group("app"):
            flush(); elements.append({"type": "appendix"}); pos = m.end()
        elif m.group("envb"):
            flush(); name = m.group("envname"); title = m.group("envtitle") or ""
            lm = re.match(r"\s*\\label\{([^}]+)\}", text[m.end():]); label = lm.group(1) if lm else ""
            j = m.end() + (lm.end() if lm else 0)
            elements.append({"type": "envbegin", "env": name, "title": title, "label": label}); pos = j
        elif m.group("enve"):
            flush(); elements.append({"type": "envend", "env": m.group("envename")}); pos = m.end()
        elif m.group("float"):
            flush(); elements.append({"type": "float", **json.loads(m.group("fpayload"))}); pos = m.end()
        elif m.group("dmb"):
            flush(); opener = m.group(0)
            if opener == "\\[": endpat = r"\\\]"; key = "display"
            else: key = re.sub(r"\*", "", m.group("dmname")); endpat = r"\\end\{" + re.escape(m.group("dmname")) + r"\}"
            em = re.compile(endpat).search(text, m.end())
            if not em: buf.append(opener); pos = m.end(); continue
            body = text[m.end():em.start()]
            labels = re.findall(r"\\label\{([^}]+)\}", body)
            numbered = not m.group("dmname", ) or not m.group("dmname").endswith("*") if m.group("dmname") else False
            lines = 1 if key in ("equation", "display", "multline") else max(1, len(re.findall(r"\\\\", body)) + 1 - len(re.findall(r"\\nonumber|\\notag", body)))
            elements.append({"type": "math", "labels": labels, "tex": body.strip(), "numbered": numbered, "count": lines if numbered else 0}); pos = em.end()
        elif m.group("input"):
            flush(); pos = m.end()
        else: pos = m.end()
    flush()
    return elements

def make_cleaner(macros):
    text_macros = {}
    for name, m in (macros or {}).items():
        if m.get("nargs", 0) == 0 and "$" not in m["body"] and "\\begin" not in m["body"]:
            body = re.sub(r"\\(?:texttt|textbf|textit|textsc|emph|mbox|text)\{([^{}]*)\}", r"\1", m["body"]).strip()
            if body and len(body) < 60 and "\\" not in body: text_macros[name] = body
    def clean(t):
        for name, body in sorted(text_macros.items(), key=lambda kv: -len(kv[0])):
            t = re.sub(re.escape(name) + r"(\{\})?(?![A-Za-z])", body, t)
        t = t.replace("~", " ").replace("\\\\", " ")
        t = re.sub(r"\\(?:noindent|centering|smallskip|medskip|bigskip|newline|quad|qquad|hfill|maketitle|clearpage|newpage|linebreak|par|indent|relax|ignorespaces|allowbreak)\b", " ", t)
        t = re.sub(r"\\(?:vspace|hspace|setlength|label|lhead|rhead|chead|thispagestyle|pagestyle|bibliographystyle|bibliography|pdfbookmark|fontsize|selectfont|addcontentsline|numberwithin)\*?\{[^}]*\}(\{[^}]*\})?", "", t)
        t = re.sub(r"\\(?:cite[pt]?|citealp|citeauthor|citeyear|citealt)\*?(?:\[[^\]]*\])?(?:\[[^\]]*\])?\{([^}]+)\}", lambda m: "[cite:" + m.group(1).replace(" ", "") + "]", t)
        t = re.sub(r"\\(?:[cC]ref|ref|eqref|autoref|pageref)\*?\{([^}]+)\}", lambda m: "[ref:" + m.group(1) + "]", t)
        t = re.sub(r"\\href\{([^}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\}", r"\2", t)
        t = re.sub(r"\\url\{([^}]*)\}", r"\1", t)
        t = re.sub(r"\\footnote\{((?:[^{}]|\{[^{}]*\})*)\}", r" (footnote: \1)", t)
        for _ in range(4):
            t = re.sub(r"\\(?:textbf|textit|emph|texttt|textsc|underline|textcolor\{[^}]*\}|mbox|text|textnormal|textup|small|footnotesize|scriptsize|large|Large|textsuperscript|textsubscript)\{((?:[^{}]|\{[^{}]*\})*)\}", r"\1", t)
        t = t.replace("``", "\u201c").replace("''", "\u201d").replace("`", "\u2018").replace("'", "\u2019")
        t = re.sub(r"\\&", "&", t); t = re.sub(r"\\%", "%", t); t = re.sub(r"\\_", "_", t); t = re.sub(r"\\#", "#", t); t = re.sub(r"\\\$", "$", t)
        t = re.sub(r"\{\\(?:bf|it|em|tt|sc|sl)\s+([^}]*)\}", r"\1", t)
        t = re.sub(r"\\(?:begin|end)\{[a-zA-Z*]+\}(?:\[[^\]]*\])?", " ", t)
        t = re.sub(r"\\item\s*(?:\[[^\]]*\])?", " • ", t)
        t = re.sub(r"\{([^{}$\\]*?):\}", r"\1:", t)   # {Goal:} → Goal:
        t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n\n", t)
        return t.strip()
    return clean

def split_sentences(t):
    prot = []
    def keep(m): prot.append(m.group(0)); return f"\x00{len(prot) - 1}\x00"
    t = re.sub(r"\$\$.*?\$\$|\$(?:[^$\\]|\\.)*\$|\\\(.*?\\\)", keep, t, flags=re.S)
    for a in ABBR: t = t.replace(a, a.replace(".", "\x01"))
    t = re.sub(r"(\d)\.(\d)", lambda m: m.group(1) + "\x01" + m.group(2), t)
    t = re.sub(r"\b([A-Z])\.\s", lambda m: m.group(1) + "\x01 ", t)  # initials
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[\u201c•\\$\x00])|(?<=[.!?][)\u201d])\s+(?=[A-Z])|\n\n", t)
    res = []
    for p in parts:
        p = p.replace("\x01", ".")
        p = re.sub(r"\x00(\d+)\x00", lambda m: prot[int(m.group(1))], p).strip()
        if p and not re.fullmatch(r"[{}\s]*", p): res.append(p)
    return res

def build(elements, clean):
    sentences = []; sec_path = []; env_stack = []; in_appendix = False; sid = 0
    counters = {}; env_ids = []; eq_counter = 0; refs = {}; sections = []
    fig_counter = {"figure": 0, "table": 0, "algorithm": 0}
    main_n = 0; app_n = 0; sub = [0, 0]; letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    def ctx():
        return {"section": " › ".join(s[1] for s in sec_path), "section_label": sec_path[-1][2] if sec_path else "", "env": env_stack[-1]["id"] if env_stack else "", "appendix": in_appendix}
    def add(kind, text, **kw):
        nonlocal sid
        sid += 1; u = {"id": f"s{sid:04d}", "kind": kind, "text": text, **ctx(), **kw}; sentences.append(u); return u
    for el in elements:
        if el["type"] == "appendix":
            in_appendix = True; sec_path = []; sub[:] = [0, 0]
        elif el["type"] == "heading":
            lvl = el["level"]; title = clean(el["title"])
            if lvl == 0 and not el["starred"]:
                sub[:] = [0, 0]
                if in_appendix: app_n += 1; num = letters[min(app_n - 1, 25)]
                else: main_n += 1; num = str(main_n)
            elif lvl == 1 and not el["starred"]:
                sub[0] += 1; sub[1] = 0; parent = [s for s in sec_path if s[0] == 0]
                num = (parent[-1][3] if parent else "") + "." + str(sub[0])
            elif lvl == 2 and not el["starred"]:
                sub[1] += 1; parent = [s for s in sec_path if s[0] == 1]
                num = (parent[-1][3] if parent else "") + "." + str(sub[1])
            else: num = ""
            sec_path = [s for s in sec_path if s[0] < lvl] + [(lvl, title, el["label"], num)]
            u = add("heading", title, level=lvl, num=num, label=el["label"])
            sections.append({"id": "sec_" + u["id"], "level": lvl, "title": title, "start": u["id"], "appendix": in_appendix, "num": num, "label": el["label"]})
            if el["label"]: refs[el["label"]] = ("App. " if in_appendix else "§") + num if num else title
        elif el["type"] == "envbegin":
            name = el["env"]
            if name == "proof":
                eid = "proof:" + (env_stack[-1]["id"] if env_stack and env_stack[-1]["env"] != "proof" else "unknown")
                if el["title"]:
                    rm = re.search(r"\\(?:[cC]ref|ref)\{([^}]+)\}", el["title"])
                    if rm: eid = "proof-of:" + rm.group(1)
                number = ""
            else:
                counters[name] = counters.get(name, 0) + 1; number = str(counters[name])
                eid = el["label"] or f"{name}:{number}"
            rec = {"env": name, "id": eid, "title": clean(el["title"]), "label": el["label"], "start": sid + 1, "number": number}
            env_stack.append(rec); env_ids.append(rec)
            head = f"{name.capitalize()} {number} {rec['title']}".strip() if name != "proof" else ("Proof " + rec["title"]).strip()
            add("envhead", head, env_name=name, env_title=rec["title"], env_number=number)
            if el["label"] and name != "proof": refs[el["label"]] = f"{name.capitalize()} {number}"
        elif el["type"] == "envend":
            if env_stack: env_stack[-1]["end"] = sid; env_stack.pop()
        elif el["type"] == "float":
            k = el["kind"]; fig_counter[k] = fig_counter.get(k, 0) + 1
            num = str(fig_counter[k]); word = {"figure": "Fig.", "table": "Table", "algorithm": "Alg."}[k]
            for lab in el["labels"]: refs[lab] = f"{word} {num}"
            caps = [clean(c) for c in el["captions"]] or [f"({k} without caption)"]
            for ci, cap in enumerate(caps):
                add("caption", cap, float=k, labels=",".join(el["labels"]), num=num, graphics=el.get("graphics", []) if ci == 0 else [], table_tex=el.get("table_tex", []) if ci == 0 else [])
        elif el["type"] == "math":
            if el["numbered"]:
                first = eq_counter + 1; eq_counter += el["count"]
                for lab in el["labels"]: refs[lab] = f"Eq. ({first})" if el["count"] == 1 else f"Eq. ({first}–{eq_counter})"
            add("math", "$$" + re.sub(r"\\label\{[^}]+\}", "", el["tex"]).strip() + "$$", labels=el["labels"])
        elif el["type"] == "text":
            for s in split_sentences(clean(el["text"])): add("sentence", s)
    for s in sentences:
        s["refs"] = re.findall(r"\[ref:([^\]]+)\]", s["text"]); s["cites"] = re.findall(r"\[cite:([^\]]+)\]", s["text"])
    return sentences, env_ids, refs, sections

def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    flat, out = sys.argv[1], sys.argv[2]
    src = open(flat).read()
    meta = {}
    if os.path.exists(flat + ".meta.json"): meta = json.load(open(flat + ".meta.json"))
    clean = make_cleaner(meta.get("macros"))
    elements = parse(src)
    sentences, envs, refs, sections = build(elements, clean)
    json.dump({"sentences": sentences, "envs": envs, "refs": refs, "sections": sections, "title": meta.get("title", ""), "macros": {k: v["body"] for k, v in meta.get("macros", {}).items() if v.get("nargs", 0) == 0 and len(v["body"]) < 200}}, open(out, "w"), ensure_ascii=False, indent=0)
    main_body = [s for s in sentences if not s["appendix"]]
    print(json.dumps({"units": len(sentences), "main_body": len(main_body), "appendix": len(sentences) - len(main_body), "envs": len(envs), "refs": len(refs)}))
    if "--listing" in sys.argv:
        lp = sys.argv[sys.argv.index("--listing") + 1]
        with open(lp, "w") as f:
            for s in sentences:
                tag = {"heading": "#", "envhead": "@", "caption": "[cap]", "math": "[eq]", "sentence": ""}[s["kind"]]
                f.write(f"{s['id']} {tag} {(s['env'] + ' | ') if s['env'] else ''}{s['text']}\n".replace("\n", " ") + "\n")

if __name__ == "__main__":
    main()
