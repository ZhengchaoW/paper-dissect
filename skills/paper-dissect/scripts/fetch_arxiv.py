#!/usr/bin/env python3
"""Fetch an arXiv paper's LaTeX source (e-print) and PDF into a work directory.

Usage: fetch_arxiv.py <arxiv-id> <workdir>
Creates <workdir>/src/ (extracted source, if the e-print is a tar/gzip) and <workdir>/paper.pdf.
Prints a JSON summary. Stdlib only.
"""
import sys, os, json, tarfile, gzip, shutil, urllib.request, io

def fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-dissect/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    aid, work = sys.argv[1], sys.argv[2]
    os.makedirs(work, exist_ok=True)
    src_dir = os.path.join(work, "src"); os.makedirs(src_dir, exist_ok=True)
    out = {"arxiv": aid, "workdir": work, "source": None, "pdf": None}
    eprint = os.path.join(work, "eprint.bin")
    try:
        fetch(f"https://arxiv.org/e-print/{aid}", eprint)
        with open(eprint, "rb") as f: head = f.read(4)
        if head[:2] == b"\x1f\x8b":
            try:
                with tarfile.open(eprint, "r:gz") as t: t.extractall(src_dir)
                out["source"] = "tar.gz"
            except tarfile.ReadError:  # single gzipped .tex
                with gzip.open(eprint, "rb") as g, open(os.path.join(src_dir, "main.tex"), "wb") as f: shutil.copyfileobj(g, f)
                out["source"] = "gz-tex"
        elif head[:4] == b"%PDF":
            shutil.copy(eprint, os.path.join(work, "paper.pdf")); out["source"] = "pdf-only"
        else:
            try:
                with tarfile.open(eprint, "r:*") as t: t.extractall(src_dir); out["source"] = "tar"
            except tarfile.ReadError:
                shutil.copy(eprint, os.path.join(src_dir, "main.tex")); out["source"] = "tex"
    except Exception as e:
        out["source_error"] = str(e)
    try:
        pdf = os.path.join(work, "paper.pdf")
        if not os.path.exists(pdf): fetch(f"https://arxiv.org/pdf/{aid}", pdf)
        out["pdf"] = pdf
    except Exception as e:
        out["pdf_error"] = str(e)
    texs = []
    for root, _, files in os.walk(src_dir):
        for fn in files:
            if fn.endswith(".tex"): texs.append(os.path.relpath(os.path.join(root, fn), src_dir))
    out["tex_files"] = len(texs)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
