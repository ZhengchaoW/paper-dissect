#!/usr/bin/env python3
"""Flatten a LaTeX project into one file: find the main .tex (contains \\begin{document}),
inline every \\input / \\include recursively, strip comments, and keep only the document body.

Usage: flatten_tex.py <src_dir> <out_flat.tex> [--main FILE]
Also writes <out>.macros.json with simple \\newcommand definitions (for text expansion and KaTeX).
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

def extract_macros(text):
    macros = {}
    for m in re.finditer(r"\\(?:re)?newcommand\*?\{?\\([A-Za-z]+)\}?(?:\[(\d)\])?\{", text):
        name, nargs = m.group(1), m.group(2)
        # read balanced body
        i = m.end(); depth = 1; body = ""
        while i < len(text) and depth:
            c = text[i]
            if c == "\\": body += text[i:i + 2]; i += 2; continue
            if c == "{": depth += 1
            elif c == "}": depth -= 1
            if depth: body += c
            i += 1
        if len(body) < 400: macros["\\" + name] = {"body": body, "nargs": int(nargs) if nargs else 0}
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
