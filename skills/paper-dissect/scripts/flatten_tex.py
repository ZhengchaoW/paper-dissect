#!/usr/bin/env python3
"""Flatten a LaTeX project into one file: find the main .tex (contains \\begin{document}),
inline every \\input / \\include recursively, strip comments, and keep only the document body.

Usage: flatten_tex.py <src_dir> <out_flat.tex> [--main FILE]
Also writes <out>.meta.json with LaTeX macro definitions (for text expansion and KaTeX).
"""
import sys, os, re, json

def strip_comments(s):
    out = []
    for line in s.split("\n"):
        i = 0; res = ""
        while i < len(line):
            ch = line[i]
            if ch == "\\" and i + 1 < len(line): res += line[i:i + 2]; i += 2; continue
            if ch == "%": break
            res += ch; i += 1
        out.append(res)
    return "\n".join(out)

def find_main(src):
    cands = []
    for root, _, files in os.walk(src):
        for fn in files:
            if fn.endswith(".tex"):
                p = os.path.join(root, fn)
                try: txt = open(p, encoding="utf-8", errors="replace").read()
                except Exception: continue
                if "\\begin{document}" in txt: cands.append((len(txt), p))
    if not cands: raise SystemExit("no .tex with \\begin{document} found")
    cands.sort(); return cands[-1][1]

def flatten(path, root, seen):
    if path in seen: return ""
    seen.add(path)
    s = strip_comments(open(path, encoding="utf-8", errors="replace").read())
    def rep(m):
        name = m.group(2).strip()
        for cand in (name + ".tex", name):
            p = os.path.normpath(os.path.join(root, cand))
            if os.path.isfile(p):
                return f"\n%%BEGININPUT {cand}\n" + flatten(p, root, seen) + f"\n%%ENDINPUT {cand}\n"
        return f"\n%%MISSING {name}\n"
    return re.sub(r"\\(input|include)\{([^}]+)\}", rep, s)

def read_group(text, start, opener="{", closer="}"):
    """Return the contents and first index after one balanced group."""
    if start >= len(text) or text[start] != opener:
        return None, start
    depth = 1; i = start + 1; body = ""
    while i < len(text) and depth:
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            body += text[i:i + 2]; i += 2; continue
        if c == opener: depth += 1
        elif c == closer: depth -= 1
        if depth: body += c
        i += 1
    return (body, i) if depth == 0 else (None, start)

def extract_macros(text):
    """Extract common command definitions in source order; later definitions win."""
    found = []
    command = r"(\\(?:[A-Za-z@]+|.))"

    new_pat = re.compile(
        r"\\(?:newcommand|renewcommand|providecommand)\*?\s*"
        r"(?:\{\s*" + command + r"\s*\}|" + command + r")"
    )
    for m in new_pat.finditer(text):
        name = m.group(1) or m.group(2)
        i = m.end()
        while i < len(text) and text[i].isspace(): i += 1
        nargs = 0
        if i < len(text) and text[i] == "[":
            raw, i2 = read_group(text, i, "[", "]")
            if raw is None or not raw.strip().isdigit(): continue
            nargs = int(raw.strip()); i = i2
            while i < len(text) and text[i].isspace(): i += 1
            # Optional default for argument 1. KaTeX receives the body and arity;
            # callers that use the optional form still render safely with throwOnError=false.
            if i < len(text) and text[i] == "[":
                _, i = read_group(text, i, "[", "]")
                while i < len(text) and text[i].isspace(): i += 1
        body, end = read_group(text, i)
        if body is not None and len(body) < 400:
            found.append((m.start(), name, body, nargs))

    def_pat = re.compile(r"\\(?:def|gdef|edef|xdef)\s*" + command)
    for m in def_pat.finditer(text):
        name = m.group(1); i = m.end(); params = ""
        while i < len(text) and text[i] != "{":
            if text[i] == "\n" or len(params) >= 200: break
            params += text[i]; i += 1
        body, end = read_group(text, i)
        if body is None or len(body) >= 400: continue
        args = [int(x) for x in re.findall(r"#([1-9])", params)]
        found.append((m.start(), name, body, max(args, default=0)))

    macros = {}
    for _, name, body, nargs in sorted(found):
        macros[name] = {"body": body, "nargs": nargs}
    return macros

def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    src, out = sys.argv[1], sys.argv[2]
    main_file = None
    if "--main" in sys.argv: main_file = os.path.join(src, sys.argv[sys.argv.index("--main") + 1])
    main_file = main_file or find_main(src)
    root = os.path.dirname(main_file)
    whole = flatten(main_file, root, set())
    macros = extract_macros(whole)
    body = whole.split("\\begin{document}", 1)[1].split("\\end{document}", 1)[0] if "\\begin{document}" in whole else whole
    # title
    tm = re.search(r"\\title\{((?:[^{}]|\{[^{}]*\})*)\}", whole)
    title = re.sub(r"\\\\|\\(?:vspace|thanks)\{[^}]*\}", " ", tm.group(1)).strip() if tm else ""
    title = re.sub(r"\s+", " ", re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", title))
    open(out, "w").write(body)
    json.dump({"macros": macros, "title": title, "main": os.path.relpath(main_file, src)}, open(out + ".meta.json", "w"), indent=1)
    print(json.dumps({"main": main_file, "chars": len(body), "macros": len(macros), "title": title}))

if __name__ == "__main__":
    main()
