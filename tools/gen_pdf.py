# -*- coding: utf-8 -*-
"""gen_pdf.py — the PDF-ONLY document pipeline (no Word). Build print-styled HTML, render to PDF via
LibreOffice headless. Version stamping (cover line + footer) comes from doc_versions.

Per the standing rule (2026-07-28): human-facing docs are generated straight to PDF; we no longer
produce .docx. Content generators build a list of section HTML strings with the small helpers here
and call render(key, sections).

  import gen_pdf as G, doc_versions as V
  body = [G.section("Overview", G.p("...") + G.table(["A","B"], rows)), ...]
  path = G.render("custodes-analysis", body)     # -> docs/.../<name>-vX.Y.pdf
"""
import html as _html
import os
import subprocess
import doc_versions as V

CSS = """
@page { size: A4; margin: 1.6cm 1.5cm; }
body { font-family: 'Liberation Sans','DejaVu Sans',sans-serif; font-size: 10pt; color:#1a1a1a; line-height:1.34; }
h1 { font-size: 20pt; margin: 0 0 2pt 0; color:#5a4a13; }
h2 { font-size: 13pt; margin: 16pt 0 4pt 0; color:#5a4a13; border-bottom:1.5px solid #c9b458; padding-bottom:2pt; }
h3 { font-size: 11pt; margin: 10pt 0 2pt 0; color:#2a2a2a; }
p  { margin: 3pt 0; }
.small { font-size: 8.5pt; color:#666; }
.cover { border-bottom:3px solid #c9b458; padding-bottom:6pt; margin-bottom:10pt; }
.cover .sub { font-size: 11pt; color:#444; margin-top:2pt; }
.cover .ver { font-size: 9.5pt; color:#8a7420; margin-top:4pt; font-weight:bold; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0; font-size: 9pt; }
th,td { border: 0.75px solid #bbb; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background:#f3edd6; color:#4a3d10; }
tr:nth-child(even) td { background:#faf8f0; }
.fav { color:#1a7a2e; font-weight:bold; } .unfav { color:#a11; font-weight:bold; } .even { color:#8a6d00; font-weight:bold; }
ul { margin: 3pt 0 3pt 16pt; padding:0; } li { margin: 1pt 0; }
.finding { background:#fff8e1; border:1px solid #c9b458; padding:6pt 9pt; margin:8pt 0; }
.footer { margin-top:14pt; border-top:1px solid #ccc; padding-top:4pt; font-size:8pt; color:#888; }
"""


def esc(s):
    return _html.escape(str(s))


def p(text):
    return f"<p>{text}</p>"


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def section(title, inner):
    return f"<h2>{esc(title)}</h2>{inner}"


def sub(title, inner):
    return f"<h3>{esc(title)}</h3>{inner}"


def table(headers, rows, classes=None):
    """rows = list of cell-lists; classes[i][j] optional CSS class per cell."""
    head = "<tr>" + "".join(f"<th>{esc(h)}</th>" for h in headers) + "</tr>"
    body = ""
    for r, row in enumerate(rows):
        tds = ""
        for c, cell in enumerate(row):
            cls = ""
            if classes and r < len(classes) and c < len(classes[r]) and classes[r][c]:
                cls = f' class="{classes[r][c]}"'
            tds += f"<td{cls}>{cell}</td>"
        body += f"<tr>{tds}</tr>"
    return f"<table>{head}{body}</table>"


def finding(text):
    return f'<div class="finding">{text}</div>'


def _cover(key):
    return (f'<div class="cover"><h1>{esc(V.title(key))}</h1>'
            f'<div class="ver">{esc(V.cover_line(key))}</div></div>')


def render(key, sections):
    """Assemble cover + sections into HTML and convert to the versioned PDF path. Returns the path."""
    out = V.out_path(key)                       # .pdf (relpath ends in .pdf)
    outdir = os.path.dirname(out)
    os.makedirs(outdir, exist_ok=True)
    doc = (f"<html><head><meta charset='utf-8'><title>{esc(V.title(key))}</title>"
           f"<style>{CSS}</style></head><body>{_cover(key)}"
           + "".join(sections)
           + f'<div class="footer">{esc(V.footer_text(key))}</div></body></html>')
    base = os.path.splitext(os.path.basename(out))[0]
    html_path = os.path.join(outdir, base + ".html")
    open(html_path, "w", encoding="utf-8").write(doc)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, html_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(html_path)                        # keep only the PDF
    produced = os.path.join(outdir, base + ".pdf")
    if produced != out and os.path.exists(produced):
        os.replace(produced, out)
    return out
