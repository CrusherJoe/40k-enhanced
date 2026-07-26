# Reports & Plans

**Publishing convention (user, 2026-07-26):** all **Word (.docx)** and **Excel (.xlsx)**
reports/plans live here — portable, shareable deliverables (distinct from the terse
`docs/*.md` working notes and `docs/meta/*.md` reference docs).

Generated from single-source-of-truth data modules in `tools/` — edit the data, re-run
the generator, never hand-edit the Office files:

| Deliverable | Generator | Data source |
|---|---|---|
| `LSO-Knights-List-and-Analysis.xlsx` | `tools/gen_lso_xlsx.py` | `tools/lso_data.py` |
| `LSO-Runbook.docx` (per-archetype battle plans) | `tools/gen_lso_runbook_docx.py` | `tools/lso_data.py` |

Regenerate both:
```
PYTHONPATH=tools python3 tools/gen_lso_xlsx.py
PYTHONPATH=tools python3 tools/gen_lso_runbook_docx.py
```

When the meta shifts (new listhammer lists, corrected verdicts), update `tools/lso_data.py`
(and `docs/meta/*.md`) and re-run — the docs stay in sync.
