#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdf_extract.py — COLUMN-AWARE PDF -> clean reading-order text.

GW rulebooks/faction packs are 2-column; `pdftotext -layout` jams the columns
side-by-side (unreadable). This uses `pdftotext -bbox-layout` (word coordinates),
detects the gutter per page, and emits the LEFT column fully then the RIGHT column
(or the whole page if it's single-column / a datasheet table). Result: text you can
grep and read without fighting the layout.

  python3 tools/pdf_extract.py <in.pdf> [-o out.txt]
  python3 tools/pdf_extract.py --batch      # re-extract every mapped source into data/
"""
import argparse, html, os, re, statistics, subprocess, sys

# batch map: source PDF (scratchpad or docs) -> committed clean-text destination
SCRATCH = os.environ.get("WH_SCRATCH", "")


def pages(pdf):
    xml = subprocess.check_output(["pdftotext", "-bbox-layout", pdf, "-"]).decode("utf-8", "ignore")
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', xml, re.S):
        w = float(pm.group(1))
        words = []
        for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>',
                             pm.group(3)):
            x0, y0, x1, y1 = map(float, m.groups()[:4])
            t = html.unescape(m.group(5)).strip()
            if t:
                words.append((x0, y0, x1, y1, t))
        yield w, words


def to_lines(words):
    """Group words into lines by yMin proximity; sort each line left-to-right."""
    if not words:
        return ""
    h = statistics.median(y1 - y0 for _, y0, x1, y1, _ in words) or 8
    thr = h * 0.6
    words = sorted(words, key=lambda a: a[1])
    lines, cur, cy = [], [], None
    for wd in words:
        if cy is None or abs(wd[1] - cy) <= thr:
            cur.append(wd)
            cy = wd[1] if cy is None else cy
        else:
            lines.append(cur); cur = [wd]; cy = wd[1]
    if cur:
        lines.append(cur)
    return "\n".join(" ".join(w[4] for w in sorted(ln, key=lambda a: a[0])) for ln in lines)


def reconstruct(page_w, words):
    if not words:
        return ""
    centers = [(x0 + x1) / 2 for x0, y0, x1, y1, _ in words]
    # find the GUTTER = the vertical band in the middle third with the fewest word-centers
    band = page_w * 0.035
    best_x, best = page_w / 2, len(words)
    x = page_w * 0.38
    while x <= page_w * 0.62:
        c = sum(1 for v in centers if abs(v - x) < band)
        if c < best:
            best, best_x = c, x
        x += page_w * 0.01
    two_col = best < 0.05 * len(words)               # a real gutter is nearly empty
    if two_col:
        left = [w for w in words if (w[0] + w[2]) / 2 < best_x]
        right = [w for w in words if (w[0] + w[2]) / 2 >= best_x]
        return to_lines(left) + "\n" + to_lines(right)
    return to_lines(words)                            # single-column page / datasheet table


def extract(pdf):
    return "\n\n".join(reconstruct(w, words) for w, words in pages(pdf)).strip() + "\n"


def build_batch():
    sp = SCRATCH or _guess_scratch()
    # (dest, [candidate source paths]) — first existing wins
    jobs = {
        "data/rules/core-rules.txt": [f"{sp}/40k_core_rules.pdf", "docs/sources/40k_core_rules.pdf"],
        "data/rules/event-companion.txt": [f"{sp}/event_companion.pdf", "docs/sources/40k_event_companion.pdf"],
    }
    fp = {"admech": "adeptus-mechanicus", "aeldari": "aeldari", "am": "astra-militarum", "ba": "blood-angels",
          "bt": "black-templars", "chaos": "chaos-space-marines", "chaosknights": "chaos-knights",
          "custodes": "adeptus-custodes", "da": "dark-angels", "daemons": "chaos-daemons", "dg": "death-guard",
          "drukhari": "drukhari", "dw": "deathwatch", "ec": "emperors-children", "gk": "grey-knights",
          "gsc": "genestealer-cults", "necrons": "necrons", "orks": "orks", "sisters": "adepta-sororitas",
          "sm": "space-marines", "sw": "space-wolves", "tau": "tau-empire", "tsons": "thousand-sons",
          "tyranids": "tyranids", "votann": "leagues-of-votann", "we": "world-eaters", "agents": "agents-of-the-imperium"}
    for stem, slug in fp.items():
        jobs[f"data/faction-packs/{slug}.txt"] = [f"{sp}/{stem}_fp.pdf", f"{sp}/{stem}fp.pdf"]
    jobs["data/faction-packs/imperial-knights.txt"] = [f"{sp}/ikfp.pdf", f"{sp}/ik_faction_pack.pdf"]

    done = miss = 0
    for dest, srcs in sorted(jobs.items()):
        src = next((s for s in srcs if os.path.exists(s)), None)
        if not src:
            print(f"# MISS (no PDF): {dest}", file=sys.stderr); miss += 1; continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            txt = extract(src)
            open(dest, "w", encoding="utf-8").write(txt)
            print(f"# {dest}: {len(txt.splitlines())} lines  (from {os.path.basename(src)})", file=sys.stderr)
            done += 1
        except Exception as e:
            print(f"# FAIL {dest}: {e}", file=sys.stderr); miss += 1
    print(f"# extracted {done}, missing {miss}", file=sys.stderr)


def _guess_scratch():
    import glob
    hits = glob.glob("/tmp/claude-*/*/*/scratchpad") + glob.glob("/tmp/claude-*/**/scratchpad", recursive=True)
    return hits[0] if hits else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--batch", action="store_true")
    a = ap.parse_args()
    if a.batch:
        build_batch(); return
    if not a.pdf:
        ap.error("give a PDF or --batch")
    txt = extract(a.pdf)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        open(a.out, "w", encoding="utf-8").write(txt)
        print(f"wrote {a.out} ({len(txt.splitlines())} lines)", file=sys.stderr)
    else:
        sys.stdout.write(txt)


if __name__ == "__main__":
    main()
