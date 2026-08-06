#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md_to_pdf.py — render a Markdown doc to a versioned, print-clean PDF via soffice.

For hand-authored human-facing docs (reviews, plans) that live as Markdown but need a PDF per
the deliverable convention. Converts a safe subset of Markdown (# / ## headings, **bold**,
`code`, - lists, | tables |, paragraphs) to soffice-safe HTML (no @page/var/float, no backgrounds
on wrapping blocks — see the lessons in bcp_dossier), stamps the version from doc_versions if a
key is given, and converts with LibreOffice.

  python3 tools/md_to_pdf.py <file.md> [doc_key]      # -> <same stem>.pdf
"""
import html as _html, os, re, subprocess, sys

CSS = """
body{font-family:'DejaVu Sans',Arial,sans-serif;color:#22262d;max-width:900px;margin:0 auto;
   padding:24px;line-height:1.45;font-size:11px}
h1{font-size:22px;margin:2px 0 2px;color:#1a1d23;border-bottom:3px solid #c69a3a;padding-bottom:5px}
.ver{font-family:'DejaVu Sans Mono',monospace;font-size:10px;color:#9a6f1c;font-weight:bold;margin:0 0 10px}
h2{font-size:15px;color:#5a4a12;border-bottom:1px solid #d8d2c4;padding-bottom:3px;margin:20px 0 8px}
p{margin:7px 0}
ul{margin:6px 0 6px 0;padding-left:20px} li{margin:3px 0}
code{font-family:'DejaVu Sans Mono',monospace;font-size:10px;color:#7a4a12}
table{border-collapse:collapse;width:100%;font-size:10px;margin:8px 0 14px}
th{background:#20242b;color:#fff;text-align:left;padding:4px 7px;font-size:9.5px}
td{padding:4px 7px;border-bottom:1px solid #e0dccf;vertical-align:top}
"""


def inline(s):
    s = _html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def md_to_html(md, ver_line=""):
    out, i, lines = [], 0, md.splitlines()
    if ver_line:
        pass  # inserted after first h1
    ul = False
    def close_ul():
        nonlocal ul
        if ul: out.append("</ul>"); ul = False
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            close_ul(); out.append(f"<h1>{inline(ln[2:])}</h1>")
            if ver_line: out.append(f"<div class='ver'>{_html.escape(ver_line)}</div>")
        elif ln.startswith("## "):
            close_ul(); out.append(f"<h2>{inline(ln[3:])}</h2>")
        elif ln.startswith("### "):
            close_ul(); out.append(f"<h2>{inline(ln[4:])}</h2>")
        elif ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[-:\s|]+\|\s*$", lines[i + 1]):
            close_ul()
            hdr = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            t = ["<table><tr>"] + [f"<th>{inline(c)}</th>" for c in hdr] + ["</tr>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</table>"); out.append("".join(t)); continue
        elif ln.strip().startswith(("- ", "* ")):
            if not ul: out.append("<ul>"); ul = True
            out.append(f"<li>{inline(ln.strip()[2:])}</li>")
        elif ln.strip() == "":
            close_ul()
        else:
            close_ul(); out.append(f"<p>{inline(ln)}</p>")
        i += 1
    close_ul()
    return f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>" + "\n".join(out) + "</body></html>"


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: md_to_pdf.py <file.md> [doc_key]")
    md_path = sys.argv[1]; doc_key = sys.argv[2] if len(sys.argv) > 2 else None
    ver_line = ""
    if doc_key:
        import doc_versions as V
        ver_line = V.cover_line(doc_key)
    html = md_to_html(open(md_path, encoding="utf-8").read(), ver_line)
    pdf_path = os.path.splitext(md_path)[0] + ".pdf"
    src = os.path.splitext(md_path)[0] + "_src.html"
    open(src, "w", encoding="utf-8").write(html)
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir",
                        os.path.dirname(pdf_path) or ".", src], check=True, capture_output=True, timeout=180)
        made = os.path.splitext(src)[0] + ".pdf"
        if made != pdf_path and os.path.exists(made):
            os.replace(made, pdf_path)
        print(f"# pdf -> {pdf_path}", file=sys.stderr)
    finally:
        if os.path.exists(src):
            os.remove(src)


if __name__ == "__main__":
    main()
