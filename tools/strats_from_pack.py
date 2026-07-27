#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""strats_from_pack.py — parse stratagems from the tournament FACTION PACK (PRIMARY source of truth).

Precedence (per the standing rule): the faction pack is authoritative for strats; 39k.pro (pull_39k.py)
is only a FALLBACK for strats/detachments a pack omits. This tool parses data/faction-packs/<slug>.txt
and writes each card into data/strats/<slug>.json tagged _src="faction-pack" — which ALWAYS wins the
merge (pull_39k never clobbers a faction-pack card).

Pack block shape (tolerant of OCR noise):
    <STRAT NAME>[ <N>CP]              <- name; CP sometimes here, sometimes buried in the lore
    <DETACHMENT> [– <TYPE>] STRATAGEM <- detachment + optional type
    <lore ...>                        <- may contain "<N>CP"
    WHEN: ...   TARGET: ...   EFFECT: ...  [RESTRICTIONS: ...]

Usage:
  python3 tools/strats_from_pack.py adeptus-custodes
  python3 tools/strats_from_pack.py --all
"""
import argparse, glob, json, os, re, sys

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PACKS = os.path.join(DATA, "faction-packs")
TYPES = {"STRATEGIC PLOY": "strategicPloy", "BATTLE TACTIC": "battleTactic",
         "WARGEAR": "wargear", "EPIC DEED": "epicDeed"}
SMALL = {"of", "the", "and", "to", "a", "in", "for"}
LABELS = ("WHEN:", "TARGET:", "EFFECT:", "RESTRICTIONS:")


def titlecase(s):
    words = s.strip().lower().split()
    return " ".join(w if (w in SMALL and i) else w.capitalize() for i, w in enumerate(words))


def clean(txt):
    return re.sub(r"\s+", " ", txt).strip()


def parse(slug):
    path = os.path.join(PACKS, slug + ".txt")
    if not os.path.exists(path):
        return {}
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8")]
    # indices of "... STRATAGEM" header lines
    heads = [i for i, l in enumerate(lines) if re.search(r"\bSTRATAGEM\b", l) and l.strip().endswith("STRATAGEM")]
    out = {}  # detachment -> {name -> card}
    for hi, i in enumerate(heads):
        hdr = lines[i].strip()
        det_raw = re.sub(r"\s*[–—-]?\s*(?:STRATEGIC PLOY|BATTLE TACTIC|WARGEAR|EPIC DEED)?\s*STRATAGEM$",
                         "", hdr).strip(" –—-")
        det = titlecase(det_raw)
        tmatch = re.search(r"(STRATEGIC PLOY|BATTLE TACTIC|WARGEAR|EPIC DEED)\s*STRATAGEM$", hdr)
        stype = TYPES.get(tmatch.group(1)) if tmatch else None
        # NAME = nearest non-empty, non-numeric line above the header
        name, cp = None, None
        j = i - 1
        while j >= 0:
            cand = lines[j].strip()
            if cand and not re.fullmatch(r"\d+", cand) and "STRATAGEM" not in cand:
                m = re.match(r"^(.*?)(?:\s+(\d+)\s*CP)?$", cand)
                name = titlecase(m.group(1)) if m.group(1).isupper() else m.group(1).strip()
                if m.group(2):
                    cp = int(m.group(2))
                break
            j -= 1
        if not name:
            continue
        # body = lines until the NEXT header's name line (or next header)
        end = heads[hi + 1] - 1 if hi + 1 < len(heads) else len(lines)
        body = lines[i + 1:end]
        blob = "\n".join(body)
        if cp is None:
            cpm = re.search(r"(\d+)\s*CP", blob)
            cp = int(cpm.group(1)) if cpm else None
        fields = _split_fields(body)
        out.setdefault(det, {})[name] = dict(
            type=stype, cp=cp, when=fields.get("WHEN:"), target=fields.get("TARGET:"),
            effect=fields.get("EFFECT:"), restrictions=fields.get("RESTRICTIONS:"))
    return out


def _split_fields(body):
    """Pull WHEN/TARGET/EFFECT/RESTRICTIONS values from a block. Labels can appear mid-line (e.g. a
    CP prefix: "1CP WHEN: ...") so split the whole blob on the labels rather than line-anchoring."""
    blob = " ".join(l.strip() for l in body if not re.fullmatch(r"\d+", l.strip()))
    parts = re.split(r"\b(WHEN|TARGET|EFFECT|RESTRICTIONS)\s*:", blob)
    fields = {}
    for k in range(1, len(parts) - 1, 2):
        fields[parts[k] + ":"] = clean(parts[k + 1])
    return {k: v for k, v in fields.items() if v}


def write(slug, parsed):
    path = os.path.join(DATA, "strats", slug + ".json")
    existing = {}
    if os.path.exists(path):
        existing = {k: v for k, v in json.load(open(path, encoding="utf-8")).items() if not k.startswith("_")}
    for det, cards in parsed.items():
        dst = dict(existing.get(det, {}))
        for name, card in cards.items():
            dst[name] = dict({k: v for k, v in card.items() if v is not None}, _src="faction-pack")
        existing[det] = dst
    payload = {"_source": "stratagems grouped by DETACHMENT. PRIMARY = faction pack (_src=faction-pack); "
                          "FALLBACK = 39k.pro (_src=39k.pro) via pull_39k.py for what the pack omits."}
    for det in sorted(existing):
        payload[det] = {k: existing[det][k] for k in sorted(existing[det])}
    os.makedirs(os.path.join(DATA, "strats"), exist_ok=True)
    json.dump(payload, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return sum(len(c) for c in parsed.values()), len(parsed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    slugs = ([os.path.splitext(os.path.basename(p))[0] for p in sorted(glob.glob(os.path.join(PACKS, "*.txt")))]
             if a.all else ([a.slug] if a.slug else []))
    if not slugs:
        ap.error("give a slug or --all")
    for s in slugs:
        parsed = parse(s)
        if not parsed:
            print(f"# {s}: no stratagems found in pack", file=sys.stderr)
            continue
        n, nd = write(s, parsed)
        print(f"{s:24} {nd:2} detachments  {n:3} strats (faction-pack, PRIMARY)")


if __name__ == "__main__":
    main()
