#!/usr/bin/env bash
# Scheduled BCP field sync. Two steps, hands-free (auto browser-login via tools/bcp_auth.py + .env.bcp):
#   1. pull any NEW current-window GTs (roster + army lists + DB)          -> tools/bcp_pull_gts.py
#   2. fill in standings for events that don't have them yet (weekend      -> tools/bcp_refresh_results.py
#      events finishing, TO posting results late)                             --incomplete-only
# Most events run on weekends, but this runs DAILY so freshly-finished events get folded in within a day.
# Does NOT auto-commit — review the diff and commit yourself (per the commit-the-DBs policy, like
# sync_bsdata.sh). Needs .env.bcp creds + the node/Playwright deps (see .env.bcp.example). Log: reports/bcp-sync.log.
set -uo pipefail

REPO="/opt/projects/wh"
cd "$REPO" || exit 1
export PYTHONPATH=src
mkdir -p reports

# rolling window: ~14 days back to a few days ahead (so this weekend's events get their rosters/lists
# pulled early; step 2 fills results once they finish). Floored at FLOOR so we never reach before the
# current-balance era (11E launched 2026-07-27) — bump FLOOR when a future dataslate resets "current".
FLOOR="2026-07-27"
START="$(date -u -d '14 days ago' +%F 2>/dev/null || date -u -v-14d +%F)"
[ "$START" \< "$FLOOR" ] && START="$FLOOR"
END="$(date -u -d '+4 days' +%F 2>/dev/null || date -u -v+4d +%F)"

{
  echo "===== BCP sync $(date -u +%FT%TZ)  window ${START}..${END} ====="
  echo "--- 1. pull new events ---"
  python3 tools/bcp_pull_gts.py --start "$START" --end "$END"
  echo "--- 2. refresh standings for incomplete events ---"
  python3 tools/bcp_refresh_results.py --incomplete-only
  echo "exit=$?  changed data/bcp files: $(git status --porcelain data/bcp | wc -l)"
} >> reports/bcp-sync.log 2>&1
