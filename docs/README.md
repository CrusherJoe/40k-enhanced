# docs/

Organized documentation for the 40k 11E force-disposition + list-optimization work.

```
docs/
├── README.md            ← you are here
├── reports/             generated deliverables (Word/Excel + PDF), versioned, by army
│   ├── knights/
│   ├── great-value/
│   └── sisters/
├── notes/               working markdown research/analysis (source thinking)
│   ├── knights/
│   ├── sisters/
│   ├── core-rules-reference.md
│   └── matched-play.md
├── meta/                per-faction archetype analyses (the observed 11E meta)
└── sources/             large GW source PDFs (gitignored) + SOURCES.md
```

## reports/ — the deliverables

Every file here is **generated** from a single-source-of-truth data module in `tools/`
(never hand-edited) and carries a **version number** on its cover, in a per-page footer,
and **in its filename** (`…-vX.Y.docx`; the current versions live in `tools/doc_versions.py`). Each **`.docx` has a matching `.pdf`**;
**`.xlsx` workbooks stay as Excel files** (no PDF/CSV export).

Versions live in **`tools/doc_versions.py`** — bump there when content changes, then
regenerate; a new `-vX.Y` file is written and the old revision is left on disk
(`doc_versions.all_stale()` lists superseded files to prune).

| Deliverable | File | Generator | Data |
|---|---|---|---|
| **LSO Runbook — Imperial Knights** (list decision + 26 per-archetype battle plans) | `reports/knights/LSO-Runbook-vX.Y.docx` | `gen_lso_runbook_docx.py` | `lso_data.py` |
| **LSO Knights — List Decision** (List A vs B, prevalence-weighted) | `reports/knights/LSO-Knights-List-Decision-vX.Y.xlsx` | `gen_lso_decision_xlsx.py` | `lso_data.py` |
| **LSO Knights — List & Analysis** (single-List-A reference) | `reports/knights/LSO-Knights-List-and-Analysis-vX.Y.xlsx` | `gen_lso_xlsx.py` | `lso_data.py` |
| **Great Value — LSO Runbook** (the friend's Imperial Fists) | `reports/great-value/GV-LSO-Runbook-vX.Y.docx` | `gen_gv_docx.py` | `gv_data.py` |
| **Great Value — LSO Analysis** | `reports/great-value/GV-LSO-Analysis-vX.Y.xlsx` | `gen_gv_xlsx.py` | `gv_data.py` + `mc_gv_sim.py` |
| **Great Value vs Knights — Full-Game Simulation** | `reports/great-value/Great-Value-vs-Knights-Full-Game-Simulation-vX.Y.docx` | `gen_greatvalue_sim_docx.py` | sim |
| **Adepta Sororitas — Battle Plan** | `reports/sisters/Sisters-Battle-Plan-vX.Y.docx` | `gen_sisters_docx.py` | army builder + layouts |
| **Adepta Sororitas — Quick Reference** | `reports/sisters/Sisters-Quick-Reference-vX.Y.docx` | `gen_sisters_qref_docx.py` | layouts |
| **Black Templars — 'Send Help' FIXED Runbook** (rescued list + tapestry + battle plans) | `reports/black-templars/BT-SendHelp-Fixed-Runbook-vX.Y.docx` | `gen_bt_docx.py` | `bt_data.py` |
| **Black Templars — 'Send Help' FIXED Analysis** (matchups + sim) | `reports/black-templars/BT-SendHelp-Fixed-Analysis-vX.Y.xlsx` | `gen_bt_xlsx.py` | `bt_data.py` + `mc_bt_sim.py` |

### Rebuild

```bash
# regenerate every deliverable from its data module
for g in gen_lso_runbook_docx gen_gv_docx gen_greatvalue_sim_docx \
         gen_lso_xlsx gen_gv_xlsx gen_lso_decision_xlsx \
         gen_sisters_docx gen_sisters_qref_docx; do
  PYTHONPATH=tools:src python3 tools/$g.py
done

# render the Word docs to PDF (needs libreoffice-writer); .xlsx stay as Excel
python3 tools/make_pdfs.py
```

## notes/ — working research

Terse markdown that feeds the data modules and deliverables. `knights/` and `sisters/`
hold list comparisons, matchup plans, mechanics; `core-rules-reference.md` and
`matched-play.md` are cross-army. These are the *thinking*, not the polished output.

## meta/ — the observed meta

One markdown per faction/archetype seen winning in the current 11E meta. These are the
reference the `lso_data.py` / `gv_data.py` matchup tapestries are distilled from.

## sources/ — GW PDFs

The large official PDFs (Core Rules, Event Companion, faction packs) are **gitignored**
to keep the repo lean — see `sources/SOURCES.md` for the re-download links. The clean,
column-aware text extraction of these lives in `data/rules/` and `data/faction-packs/`
(committed; produced by `tools/pdf_extract.py`).
