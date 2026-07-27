#!/usr/bin/env bash
# listhammer accumulator — system-crontab entry point.
# Single robots-safe SSR page-1 pull, appended (deduped) to the archive. Logs to
# logs/listhammer-cron.log with a timestamp. Does NOT git-commit (you review/commit).
# Installed schedule: Sun hourly (17 * * * 0) + Mon-Sat 12h (23 5,17 * * 1-6).
set -o pipefail
cd /opt/projects/wh || exit 1
mkdir -p logs
{
  printf '\n===== %s =====\n' "$(date -Is)"
  /usr/bin/python3 tools/listhammer_pull.py --pages 1 --store data/listhammer_archive.json
} >> logs/listhammer-cron.log 2>&1
