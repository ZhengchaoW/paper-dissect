#!/usr/bin/env python3
"""Render graph.json into the interactive reader (single self-contained HTML).

Usage: render_html.py <graph.json> <out.html> [--src-dir DIR] [--no-images] [--max-image-kb N] [--artifact]
  --src-dir   LaTeX source directory: figures referenced by \\includegraphics are embedded as data URIs
              (png/jpg/gif directly; pdf/eps via `pdftoppm` when available), tables (tabular) are converted to HTML.
  --artifact  emit the page without <!doctype>/<html>/<head>/<body> (for hosts that add their own skeleton).
Stdlib only. KaTeX is loaded from cdnjs at view time; its CSS (fonts stripped) is inlined from katex.nofonts.css.
"""
import sys, os, re, json, base64, subprocess, tempfile, html

HERE = os.path.dirname(os.path.abspath(__file__))

def find_asset(src_dir, path):
    cands = [path] + [path + ext for ext in (".png", ".jpg", ".jpeg", ".pdf", ".eps", ".gif")]
    for c in cands:
        p = os.path.join(src_dir, c)
        if os.path.isfile(p): return p
    # search by basename
    base = os.path.basename(path)
    for root, _, files in os.walk(src_dir):
        for fn in files:
            if fn == base or fn.rsplit(".", 1)[0] == base.rsplit(".", 1)[0]: return os.path.join(root, fn)
    return None

def to_data_uri(p, max_bytes=900_000):
    ext = p.rsplit(".", 1)[-1].lower()
    if ext in ("png", "jpg", "jpeg", "gif"):
        data = open(p, "rb").read()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}[ext]
    elif ext in ("pdf", "eps"):
        try:
            with tempfile.TemporaryDirectory() as td:
                out = os.path.join(td, "fig")
                subprocess.run(["pdftoppm", "-png", "-r", "110", "-singlefile", p, out], check=True, capture_output=True, timeout=60)
                data = open(out + ".png", "rb").read(); mime = "image/png"
        except Exception:
            return None
    else:
        return None
    if len(data) > max_bytes:
        data, mime = shrink(data, max_bytes)
        if data is None: return None
    return f"data:{mime};base64," + base64.b64encode(data).decode()

def shrink(data, max_bytes):
    """Downscale/re-encode with Pillow when available; otherwise give up on this image."""
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(data)); im.load()
        if im.mode not in ("RGB", "L"): im = im.convert("RGB")
        for width, q in ((1400, 82), (1100, 78), (900, 72), (700, 65)):
            if im.width > width: im2 = im.resize((width, int(im.height * width / im.width)))
            else: im2 = im
            buf = io.BytesIO(); im2.save(buf, "JPEG", quality=q, optimize=True)
            if buf.tell() <= max_bytes: return buf.getvalue(), "image/jpeg"
        return None, None
    except Exception:
        return None, None

def tabular_to_html(tex):
    body = re.sub(r"\\begin\{tabular[x*]?\}(\{[^}]*\})?(\{[^}]*\})?", "", tex, count=1)
    body = re.sub(r"\\end\{tabular[x*]?\}", "", body)
    body = re.sub(r"\\(?:toprule|midrule|bottomrule|hline|cmidrule(?:\([^)]*\))?\{[^}]*\}|cline\{[^}]*\})", "", body)
    body = re.sub(r"\\(?:small|footnotesize|scriptsize|centering|resizebox\{[^}]*\}\{[^}]*\})", "", body)
    rows = [r for r in re.split(r"\\\\", body) if r.strip()]
    out = ["<table>"]
    for i, r in enumerate(rows):
        cells = []
        for c in r.split("&"):
            c = c.strip()
            m = re.match(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}$", c, flags=re.S)
            span = ""
            if m: span = f' colspan="{m.group(1)}"'; c = m.group(2)
            m2 = re.match(r"\\multirow\{(\d+)\}\{[^}]*\}\{(.*)\}$", c, flags=re.S)
            if m2: c = m2.group(2)
            c = re.sub(r"\\(?:textbf|textit|emph|mathbf|underline|texttt)\{([^{}]*)\}", r"\1", c)
            c = re.sub(r"\\(?:cellcolor|color)\{[^}]*\}", "", c)
            c = c.replace("\\%", "%").replace("\\&", "&").replace("\\_", "_").replace("~", " ").replace("$", "")
            tag = "th" if i == 0 else "td"
            cells.append(f"<{tag}{span}>{html.escape(c)}</{tag}>")
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</table>")
    return "\n".join(out)

def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    gpath, out = sys.argv[1], sys.argv[2]
    src_dir = sys.argv[sys.argv.index("--src-dir") + 1] if "--src-dir" in sys.argv else None
    G = json.load(open(gpath))
    embedded = 0; tables = 0; skipped = 0
    max_kb = int(sys.argv[sys.argv.index("--max-image-kb") + 1]) if "--max-image-kb" in sys.argv else 900
    for s in G["sentences"]:
        if s.get("kind") != "caption": continue
        if src_dir and "--no-images" not in sys.argv:
            uris = []
            for gpath_ in s.get("graphics", [])[:6]:
                p = find_asset(src_dir, gpath_)
                if p:
                    u = to_data_uri(p, max_kb * 1000)
                    if u: uris.append(u); embedded += 1
                    else: skipped += 1
            s["graphics_data"] = uris
        s["table_html"] = [tabular_to_html(t) for t in s.get("table_tex", [])]
        tables += len(s["table_html"])
        s.pop("table_tex", None)
    template = open(os.path.join(HERE, "template.html")).read()
    css = open(os.path.join(HERE, "katex.nofonts.css")).read()
    data = json.dumps(G, ensure_ascii=False).replace("</", "<\\/")
    page = template.replace("/*KATEX_CSS*/", css).replace("/*GRAPH_JSON*/", data)
    if "--artifact" not in sys.argv:
        page = "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">" + page.replace("<title>", "", 1).replace("</title>", "", 1) + "</body></html>"
        # move the title tag into head properly
        tm = re.search(r"^(.*?)<link", page, flags=re.S)
        page = re.sub(r"<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">Paper Dissected", "<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Paper Dissected</title>", page, count=1)
        page = page.replace("</style>\n\n<div class=\"app\">", "</style></head><body style=\"margin:0\">\n<div class=\"app\">", 1)
    open(out, "w").write(page)
    print(json.dumps({"out": out, "bytes": len(page), "figures_embedded": embedded, "figures_skipped_too_large": skipped, "tables": tables, "nodes": len(G["nodes"]), "edges": len(G["edges"])}))

if __name__ == "__main__":
    main()
