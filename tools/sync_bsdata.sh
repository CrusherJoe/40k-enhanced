#!/usr/bin/env bash
# Scheduled BSData 11e sync -> local DB rebuild. Pulls the BSData catalogue and rebuilds
# data/bsdata/<slug>.json (profiles) + data/bsdata/rules/<slug>.json (ability/detachment TEXT the
# tapestry depends on). Does NOT touch MFM (points; Dataslate-driven) and does NOT auto-commit —
# review the diff and commit yourself (per the commit-the-DBs policy).
#
# Point at a fork ("the one in my git") by exporting WH_BSDATA_URL before the run, or edit the default.
# Installed as a daily system cron by the assistant; log at reports/bsdata-sync.log.
set -uo pipefail

REPO="/opt/projects/wh"
export WH_BSDATA_URL="${WH_BSDATA_URL:-https://github.com/BSData/wh40k-11e.git}"

cd "$REPO" || exit 1
mkdir -p reports
{
  echo "===== BSData sync $(date -u +%FT%TZ)  (src=$WH_BSDATA_URL) ====="
  python3 tools/refresh.py --bsdata
  echo "exit=$?  changed bsdata files: $(git status --porcelain data/bsdata | wc -l)"
} >> reports/bsdata-sync.log 2>&1
