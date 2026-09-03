#!/usr/bin/env python3
"""One command from a paper to the reading listing.

Usage:
  prepare.py <arxiv-id | source-dir | file.pdf> <workdir>

Produces in <workdir>:
  src/            LaTeX source (when available)     paper.pdf   (when available)
  flat.tex        flattened body                    skeleton.json  sentence-level units + structure
  listing.txt     the paper as numbered units — READ THIS, it is what you dissect
Falls back to pdftotext segmentation when no LaTeX source exists (lower quality: no environments, refs, or figures).
"""
import sys, os, re, json, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr); raise SystemExit(f"failed: {' '.join(cmd)}")
    return r.stdout

def pdf_fallback(pdf, work):
    txt = os.path.join(work, "paper.txt")
    run(["pdftotext", "-layout", pdf, txt])
    raw = open(txt, errors="replace").read()
    sys.path.insert(0, HERE)
    from parse_tex import split_sentences
    units = []; sid = 0; section = ""; appendix = False; sections = []
    for para in re.split(r"\n\s*\n", raw):
        p = re.sub(r"\s+", " ", para).strip()
        if not p or len(p) < 3: continue
        hm = re.match(r"^(?:(\d+(?:\.\d+)*)|([A-Z](?:\.\d+)*))\s+([A-Z][^.]{2,80})$", p)
        if hm:
            num = hm.group(1) or hm.group(2); title = hm.group(3); level = num.count(".")
            if hm.group(2): appendix = True
            sid += 1; units.append({"id": f"s{sid:04d}", "kind": "heading", "text": title, "level": level, "num": num, "section": title, "section_label": "", "env": "", "appendix": appendix, "refs": [], "cites": []})
            sections.append({"id": f"sec_s{sid:04d}", "level": level, "title": title, "start": f"s{sid:04d}", "appendix": appendix, "num": num, "label": ""}); section = title
            continue
        for s in split_sentences(p):
            sid += 1; units.append({"id": f"s{sid:04d}", "kind": "sentence", "text": s, "section": section, "section_label": "", "env": "", "appendix": appendix, "refs": [], "cites": []})
    json.dump({"sentences": units, "envs": [], "refs": {}, "sections": sections, "title": "", "macros": {}}, open(os.path.join(work, "skeleton.json"), "w"), ensure_ascii=False)
    with open(os.path.join(work, "listing.txt"), "w") as f:
        for u in units: f.write(f"{u['id']} {'#' if u['kind'] == 'heading' else ''} {u['text']}\n")
    return len(units)

def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    target, work = sys.argv[1], sys.argv[2]
    os.makedirs(work, exist_ok=True)
    src = None; pdf = None
    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", target) or re.fullmatch(r"[a-z\-]+/\d{7}", target):
        print(run([sys.executable, os.path.join(HERE, "fetch_arxiv.py"), target, work]))
        src = os.path.join(work, "src"); pdf = os.path.join(work, "paper.pdf")
    elif os.path.isdir(target): src = target
    elif target.lower().endswith(".pdf"): pdf = target
    else: raise SystemExit("give an arXiv id, a LaTeX source directory, or a PDF")
    have_tex = src and any(fn.endswith(".tex") for _, _, fs in os.walk(src) for fn in fs)
    if have_tex:
        flat = os.path.join(work, "flat.tex")
        print(run([sys.executable, os.path.join(HERE, "flatten_tex.py"), src, flat]))
        print(run([sys.executable, os.path.join(HERE, "parse_tex.py"), flat, os.path.join(work, "skeleton.json"), "--listing", os.path.join(work, "listing.txt")]))
        mode = "latex"
    elif pdf and os.path.exists(pdf) and shutil.which("pdftotext"):
        n = pdf_fallback(pdf, work); mode = "pdf-text"; print(json.dumps({"units": n}))
    else:
        raise SystemExit("no LaTeX source and no pdftotext available")
    sk = json.load(open(os.path.join(work, "skeleton.json")))
    main_body = sum(1 for s in sk["sentences"] if not s["appendix"])
    print(json.dumps({"mode": mode, "workdir": work, "units": len(sk["sentences"]), "main_body_units": main_body, "appendix_units": len(sk["sentences"]) - main_body, "environments": len(sk.get("envs", [])), "title": sk.get("title", "")}, indent=1))
    print(f"\nNext: read {os.path.join(work, 'listing.txt')} from the top, then write {os.path.join(work, 'dissection.py')} (see references/dsl.md and examples/), run it, fix until build() reports no problems, then render_html.py.")

if __name__ == "__main__":
    main()
