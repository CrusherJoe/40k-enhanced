#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""refresh.py — rebuild the local data/ database after a Dataslate drops.

Steps:
  1. clone/pull BSData/wh40k-11e (profiles source)   -> data/_src/wh40k-11e
     (override the repo with WH_BSDATA_URL=... to sync from a fork — "the one in my git")
  2. rebuild data/bsdata/<slug>.json (all factions)  via tools/bsdata_db.py
  3. rebuild data/bsdata/rules/<slug>.json           via tools/bsdata_rules.py  (ABILITY/detachment TEXT
     the tapestry depends on — kept in lockstep with the profiles)
  4. (--mfm / all) rebuild data/mfm/<slug>.json      via tools/mfm_db.py (live SSR)
Then: re-verify dataslate-touched values, regenerate reports (tools/gen_lso_*.py),
and bump the listhammer post-dataslate cutoff date in data/README.md + the analysis.

Usage:
  python3 tools/refresh.py            # everything (BSData profiles+rules + MFM)
  python3 tools/refresh.py --mfm      # only MFM
  python3 tools/refresh.py --bsdata   # only BSData profiles + rules  (the scheduled sync job runs this)
"""
import argparse, os, subprocess, sys, time

BSDATA_SRC = "data/_src/wh40k-11e"
# The BSData 11e catalogue source. Override with WH_BSDATA_URL to sync from a fork ("the one in my git").
BSDATA_URL = os.environ.get("WH_BSDATA_URL", "https://github.com/BSData/wh40k-11e.git")


def run(cmd, check=False, **kw):
    print("$ " + " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd, check=check, **kw)


def sync_bsdata():
    """Pull the BSData 11e catalogue into data/_src/wh40k-11e. Robust to the dir existing as a plain
    (gitignored) copy with no .git: initialise it as a clone of BSDATA_URL in place, then fast-forward."""
    git_dir = os.path.join(BSDATA_SRC, ".git")
    if os.path.isdir(git_dir):
        run(["git", "-C", BSDATA_SRC, "pull", "--ff-only"], check=True)
    elif os.path.isdir(BSDATA_SRC):
        # existing non-git copy -> adopt it as a working tree of BSDATA_URL without deleting local files
        run(["git", "-C", BSDATA_SRC, "init", "-q"], check=True)
        run(["git", "-C", BSDATA_SRC, "remote", "add", "origin", BSDATA_URL], check=False)
        run(["git", "-C", BSDATA_SRC, "fetch", "--depth", "1", "origin", "HEAD"], check=True)
        run(["git", "-C", BSDATA_SRC, "reset", "--hard", "FETCH_HEAD"], check=True)
    else:
        os.makedirs(os.path.dirname(BSDATA_SRC), exist_ok=True)
        run(["git", "clone", "--depth", "1", BSDATA_URL, BSDATA_SRC], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mfm", action="store_true", help="only MFM")
    ap.add_argument("--bsdata", action="store_true", help="only BSData")
    a = ap.parse_args()
    do_all = not (a.mfm or a.bsdata)

    if do_all or a.bsdata:
        print("== BSData (profiles + rules) ==", file=sys.stderr)
        sync_bsdata()
        run([sys.executable, "tools/bsdata_db.py", "--all"], check=True)
        # rules DB (army/detachment/datasheet ABILITY text) — the tapestry depends on it, so keep it in
        # lockstep with the profiles on every sync.
        run([sys.executable, "tools/bsdata_rules.py", "--all"], check=True)

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
