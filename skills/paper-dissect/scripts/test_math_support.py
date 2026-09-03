#!/usr/bin/env python3
"""Regression checks for extraction, source cleanup, and offline math rendering."""
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

def load_parse():
    path = os.path.join(HERE, "parse_tex.py")
    spec = importlib.util.spec_from_file_location("parse_tex", path)
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

    clean = load_parse().make_cleaner({})
    frontmatter = clean(r"""
        \begingroup
        \renewcommand\thefootnote{}\footnotetext{\textsuperscript{*}Equal contribution:
        \url{one@example.edu}, \url{two@example.edu}}
        \endgroup
    """)
    assert frontmatter == "*Equal contribution: one@example.edu, two@example.edu"
    assert clean(frontmatter) == frontmatter

    formulas = clean(r"""
        The medial axis uses $\#A$ and
        $$\Sigma:=\{x:\#\{y\in P(x)\}>1\}.$$
        Also $f(x)=\begin{cases}x,&x>0\\0,&x\leq0\end{cases}$.
        A label is $\text{Case:}$.
    """)
    assert r"$\#A$" in formulas and r":\#\{" in formulas
    assert r"\begin{cases}" in formulas and r"\end{cases}" in formulas
    assert clean(formulas) == formulas

    display_note = clean(r"Result: $$x=1.\footnote{See $m_t$ for details.}$$")
    assert display_note == r"Result: $$x=1.$$ (footnote: See $m_t$ for details.)"

    graph = {
        "sentences": [{
            "id": "s0001", "kind": "sentence",
            "text": r"\begingroup\renewcommand\thefootnote{}\footnotetext{*Equal contribution: one@example.edu}\endgroup",
            "assign": {"kind": "discard", "reason": "courtesy"},
            "appendix": False,
        }, {
            "id": "s0002", "kind": "sentence",
            "text": formulas,
            "assign": {"kind": "discard", "reason": "illustration"},
            "appendix": False,
        }], "envs": {}, "refs": {}, "sections": [], "nodes": [],
        "edges": [], "macros": {k: v["body"] for k, v in macros.items()},
        "meta": {"dissected_through": "s0002"},
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
        assert '"display_text": "*Equal contribution: one@example.edu"' in page
        assert "throwOnError: true" in page and "math-fallback" in page

        # Execute the exact template cleanText implementation: prose/ref cleanup
        # must be unable to mutate math after the KaTeX preflight has passed.
        template = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
        math_start = template.index("function mathPattern()")
        math_end = template.index("\nfunction renderMath", math_start)
        clean_start = template.index("function cleanText(t)")
        clean_end = template.index("\nfunction sourceText", clean_start)
        probe = r"A label is $\text{Case:}$."
        runtime_test = (
            "const TYPEWORD=/(?!)/g;"
            "function shortRef(k){return k;}function refLabel(k){return k;}"
            + template[math_start:math_end]
            + template[clean_start:clean_end]
            + "process.stdout.write(cleanText(" + json.dumps(probe) + "));"
        )
        result = subprocess.run(
            ["node", "-e", runtime_test], text=True, capture_output=True, check=True,
        )
        assert result.stdout == probe

        subprocess.run(
            ["node", os.path.join(HERE, "check_math.js"), graph_path],
            check=True,
        )

        bad_path = os.path.join(work, "bad.json")
        bad = dict(graph)
        bad["sentences"] = [dict(graph["sentences"][1], text="Bad $#A$.")]
        with open(bad_path, "w", encoding="utf-8") as f:
            json.dump(bad, f)
        result = subprocess.run(
            ["node", os.path.join(HERE, "check_math.js"), bad_path],
            text=True, capture_output=True,
        )
        assert result.returncode == 1 and "unescaped literal #" in result.stderr
    print("math support checks passed")

if __name__ == "__main__":
    main()
