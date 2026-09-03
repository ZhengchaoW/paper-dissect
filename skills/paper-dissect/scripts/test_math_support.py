#!/usr/bin/env python3
"""Small regression checks for macro extraction and offline math rendering."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

def load_flatten():
    path = os.path.join(HERE, "flatten_tex.py")
    spec = importlib.util.spec_from_file_location("flatten_tex", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    flatten = load_flatten()
    macros = flatten.extract_macros(r"""
        \newcommand{\RR}{\mathbb{R}}
        \newcommand{\pair}[2]{\langle #1,#2\rangle}
        \def\bx{\mathbf{x}}
        \def\<{\langle}
        \renewcommand{\RR}{\mathbb R}
    """)
    assert macros["\\RR"] == {"body": r"\mathbb R", "nargs": 0}
    assert macros["\\pair"] == {"body": r"\langle #1,#2\rangle", "nargs": 2}
    assert macros["\\bx"] == {"body": r"\mathbf{x}", "nargs": 0}
    assert macros["\\<"] == {"body": r"\langle", "nargs": 0}

    graph = {
        "sentences": [], "envs": {}, "refs": {}, "sections": [], "nodes": [],
        "edges": [], "macros": {k: v["body"] for k, v in macros.items()},
        "meta": {"dissected_through": "s0000"},
    }
    with tempfile.TemporaryDirectory() as work:
        graph_path = os.path.join(work, "graph.json")
        out_path = os.path.join(work, "index.html")
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(graph, f)
        subprocess.run([sys.executable, os.path.join(HERE, "render_html.py"), graph_path, out_path], check=True)
        page = open(out_path, encoding="utf-8").read()
        assert "cdnjs.cloudflare" not in page and "fonts.googleapis.com" not in page
        assert "data:font/woff2;base64," in page
        assert "/*KATEX_JS*/" not in page and "window.katex" in page
        assert "text.includes('\\\\(')" in page and "text.includes('\\\\[')" in page
        assert r"|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|" in page
    print("math support checks passed")

if __name__ == "__main__":
    main()
