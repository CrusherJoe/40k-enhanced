#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_pdfs.py — render every human-facing Word/Excel doc to a sibling PDF.

Uses LibreOffice headless (soffice --convert-to pdf), which correctly renders
the version footer + Page N-of-M fields and the xlsx print headers/footers.
The PDF lands next to its source (docs/…/Foo.docx -> docs/…/Foo.pdf).

  python3 tools/make_pdfs.py            # convert all .docx/.xlsx under docs/
  python3 tools/make_pdfs.py a.docx b.xlsx   # convert specific files
"""
import glob, os, shutil, subprocess, sys, tempfile

DOCS_DIR = "docs"


def _soffice():
    for c in ("soffice", "libreoffice"):
        if shutil.which(c):
            return c
    sys.exit("ERROR: LibreOffice (soffice/libreoffice) not found — needed for PDF export.")


def targets(argv):
    if argv:
        return [a for a in argv if a.lower().endswith((".docx", ".xlsx"))]
    out = []
    for ext in ("docx", "xlsx"):
        out += glob.glob(f"{DOCS_DIR}/**/*.{ext}", recursive=True)
    return sorted(f for f in out if not os.path.basename(f).startswith("~$"))


def convert(files):
    soffice = _soffice()
    ok, fail = 0, 0
    # isolated profile so headless conversion is reliable and doesn't clash with a running LO
    with tempfile.TemporaryDirectory() as profile:
        for f in files:
            outdir = os.path.dirname(f) or "."
            try:
                subprocess.run(
                    [soffice, "--headless", f"-env:UserInstallation=file://{profile}",
                     "--convert-to", "pdf", "--outdir", outdir, f],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=180)
                pdf = os.path.splitext(f)[0] + ".pdf"
                if os.path.exists(pdf):
                    print(f"# {pdf}  ({os.path.getsize(pdf)//1024} KB)")
                    ok += 1
                else:
                    print(f"# FAIL (no output): {f}", file=sys.stderr); fail += 1
            except subprocess.CalledProcessError as e:
                print(f"# FAIL {f}: {e.stderr.decode('utf-8','ignore')[:200]}", file=sys.stderr); fail += 1
            except subprocess.TimeoutExpired:
                print(f"# FAIL {f}: timeout", file=sys.stderr); fail += 1
    print(f"# converted {ok}, failed {fail}", file=sys.stderr)
    return fail == 0


if __name__ == "__main__":
    files = targets(sys.argv[1:])
    if not files:
        sys.exit("no .docx/.xlsx files found")
    sys.exit(0 if convert(files) else 1)
