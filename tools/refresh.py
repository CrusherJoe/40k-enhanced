#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""refresh.py — rebuild the local data/ database after a Dataslate drops.

Steps:
  1. clone/pull BSData/wh40k-11e (profiles source)   -> data/_src/wh40k-11e
  2. rebuild data/bsdata/<slug>.json (all factions)  via tools/bsdata_db.py
  3. rebuild data/mfm/<slug>.json (all factions)     via tools/mfm_db.py (live SSR)
Then: re-verify dataslate-touched values, regenerate reports (tools/gen_lso_*.py),
and bump the listhammer post-dataslate cutoff date in data/README.md + the analysis.

Usage:
  python3 tools/refresh.py            # everything
  python3 tools/refresh.py --mfm      # only MFM
  python3 tools/refresh.py --bsdata   # only BSData
"""
import argparse, os, subprocess, sys, time

BSDATA_SRC = "data/_src/wh40k-11e"
BSDATA_URL = "https://github.com/BSData/wh40k-11e.git"


def run(cmd, **kw):
    print("$ " + " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd, **kw)


def sync_bsdata():
    if os.path.isdir(os.path.join(BSDATA_SRC, ".git")):
        run(["git", "-C", BSDATA_SRC, "pull", "--depth", "1", "--ff-only"])
    else:
        os.makedirs(os.path.dirname(BSDATA_SRC), exist_ok=True)
        run(["git", "clone", "--depth", "1", BSDATA_URL, BSDATA_SRC])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mfm", action="store_true", help="only MFM")
    ap.add_argument("--bsdata", action="store_true", help="only BSData")
    a = ap.parse_args()
    do_all = not (a.mfm or a.bsdata)

    if do_all or a.bsdata:
        print("== BSData (profiles) ==", file=sys.stderr)
        sync_bsdata()
        run([sys.executable, "tools/bsdata_db.py", "--all"])

    if do_all or a.mfm:
        print("== MFM (points/DP/enhancements) ==", file=sys.stderr)
        slugs = subprocess.check_output([sys.executable, "tools/mfm_db.py", "--list"]).decode().split()
        for i, slug in enumerate(slugs):
            run([sys.executable, "tools/mfm_db.py", slug])
            if i < len(slugs) - 1:
                time.sleep(1.5)  # be polite to the MFM host

    print("\n# refresh complete. Next: re-verify dataslate-touched values, regenerate "
          "reports (tools/gen_lso_*.py), bump the listhammer cutoff date.", file=sys.stderr)


if __name__ == "__main__":
    main()
