# Reports & Plans

**Publishing convention (user, 2026-07-26):** all **Word (.docx)** and **Excel (.xlsx)**
reports/plans live here — portable, shareable deliverables (distinct from the terse
`docs/*.md` working notes and `docs/meta/*.md` reference docs).

Generated from single-source-of-truth data modules in `tools/` — edit the data, re-run
the generator, never hand-edit the Office files:

| Deliverable | Generator | Data source |
|---|---|---|
| `LSO-Knights-List-Decision.xlsx` ★ 2 Castellan/1 Lancer vs 1 Castellan/2 Lancer, grounded in the n=75 winners' meta + verified 11E profiles | `tools/gen_lso_decision_xlsx.py` | `tools/lso_data.py` |
| `LSO-Runbook.docx` (list decision + per-archetype battle plans, each annotated with the better list) | `tools/gen_lso_runbook_docx.py` | `tools/lso_data.py` |
| `LSO-Knights-List-and-Analysis.xlsx` (single-list-A reference) | `tools/gen_lso_xlsx.py` | `tools/lso_data.py` |
| `GV-LSO-Runbook.docx` + `GV-LSO-Analysis.xlsx` (the friend's **Great Value** / Imperial Fists list — same sim/workup treatment) | `tools/gen_gv_docx.py` / `tools/gen_gv_xlsx.py` | `tools/gv_data.py` + `tools/mc_gv_sim.py` |

Regenerate all:
```
PYTHONPATH=tools python3 tools/gen_lso_decision_xlsx.py
PYTHONPATH=tools python3 tools/gen_lso_runbook_docx.py
PYTHONPATH=tools python3 tools/gen_lso_xlsx.py
```

Meta data source: `data/listhammer_archive.json` (n=79), accumulated via `tools/listhammer_pull.py`
(`--from-json data/listhammer_api_dumps/*` for the human-fetched /api/ backfill + the SSR cron for ongoing).

When the meta shifts (new listhammer lists, corrected verdicts), update `tools/lso_data.py`
(and `docs/meta/*.md`) and re-run — the docs stay in sync.
