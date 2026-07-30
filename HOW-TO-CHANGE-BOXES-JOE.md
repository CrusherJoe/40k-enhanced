# 🛡️ THIS IS HOW YOU CHANGE BOXES, JOE

Everything we built lives in **git** (`github.com/CrusherJoe/40k-enhanced`, branch `main`).
Moving to a new Ubuntu box + new Claude account is: **push from the old box → clone on the new
one → run 4 commands.** That's it. This file is the whole procedure, written for you.

---

## STEP 0 — On the OLD box: make sure everything's pushed

Open a terminal in the project (`/opt/projects/wh`) and run:

```bash
cd /opt/projects/wh
git status
```

- If it says **"nothing to commit, working tree clean"** and **"Your branch is up to date with 'origin/main'"** → you're safe to leave. ✅
- If it lists changed files or says **"ahead of 'origin/main'"**, push them first:

```bash
git add -A && git commit -m "final sync before box move" && git push origin main
```

> You do **not** need to copy any files by hand. You do **not** need the `.env.bcp` token,
> the `reports/` folder, or anything under `data/_src/` — those rebuild on the new box.

---

## STEP 1 — On the NEW box: install the prerequisites

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-pip libreoffice-calc libreoffice-writer
```

(`libreoffice` gives you `soffice`, which is what turns the dossier into a PDF.)

---

## STEP 2 — Clone the project

```bash
cd /opt/projects        # or wherever you want it; the tools don't care about the path
git clone https://github.com/CrusherJoe/40k-enhanced.git wh
cd wh
pip install -r requirements.txt
```

The moment this finishes you already have **everything** — all the data, the whole LSO field,
the sim, every tool, and the project's memory. Nothing else is hiding on the old box.

---

## STEP 3 — Rebuild the reports (optional — they come with the clone)

The finished, versioned deliverables are committed under `docs/reports/knights/`, so they're
already there after STEP 2 — you can just open them. Re-run the four commands below only if you
want to regenerate (e.g. after a data refresh). Steps 1–2 rebuild the local DB + index (those are
gitignored); steps 3–4 rewrite the versioned deliverables:

```bash
export PYTHONPATH=src

# 1) the list database (from the 324 raw lists that ARE in git)
python3 tools/bcp_db.py build data/bcp/lso2026-lists/_raw --db data/bcp/lso2026.sqlite --roster data/bcp/lso2026.json

# 2) the archetype record + player lookup
python3 tools/bcp_archetypes.py build

# 3) the dossier: markdown + Excel + PDF   (this one takes the ~5 min — it's simming the field)
python3 tools/bcp_dossier.py death_rnr --min 1

# 4) the interactive field guide (HTML)
python3 tools/make_fieldguide.py
```

Your deliverables are now in **`docs/reports/knights/`**, each with a version number in the name:
- `death_rnr-LSO-Field-Dossier-v2.0.pdf` — the printable dossier
- `death_rnr-LSO-Field-Analysis-v2.0.xlsx` — the Excel
- `death_rnr-LSO-Field-Guide-v2.0.html` — the interactive field guide
- `death_rnr-LSO-Roster-v2.0.html` — the linked player roster

(The version number means a re-run with bumped content never overwrites the old one — you won't
lose track. The top-level `reports/` folder is just throwaway build scratch.)

---

## STEP 4 — Check it worked

```bash
export PYTHONPATH=src
python3 tools/bcp_archetypes.py who "Beddoe"          # should print YOUR list + verdict
python3 -m wh.sim.runbook knights custodes --games 30 # should print a runbook (READ: FAVOURED…)
```

If both print sensible output, the move is done. ✅

---

## The two things that DON'T come across automatically (and how to handle them)

1. **The field guide's web link.** The interactive field guide was published to *my old
   Claude account*, so that URL won't work from the new account. **The file itself travels fine**
   — after STEP 3 you have `docs/reports/knights/death_rnr-LSO-Field-Guide-v2.0.html` locally. On the new account just
   ask Claude to **"publish the field guide as an artifact"** and you'll get a fresh link. (Or
   just open the HTML file in a browser — it works offline, no server needed.)

2. **My memory of this project.** A new Claude account starts with a blank memory — but that's
   fine, because everything I learned is written into **`MEMORY.md`** in the repo. When you start
   the first session on the new box, tell Claude:

   > *"Read MEMORY.md, README.md, and the READMEs in data/ and data/bcp/ before we start."*

   That brings the new Claude fully up to speed — the data laws, the whole LSO pipeline, your
   `death_rnr` list, all of it.

---

## When GW drops a new dataslate (later — NOT part of moving)

Only when the game itself updates (new points/rules), refresh the data:

```bash
git clone --depth 1 https://github.com/BSData/wh40k-11e data/_src/wh40k-11e
python3 tools/refresh.py
```

Then re-run STEP 3 to rebuild the reports with the new numbers.

---

## If you want to pull a DIFFERENT tournament's lists later

You'll need a fresh BestCoastPairings token (they expire hourly). The full procedure — where to
get the token and the commands — is in **`data/bcp/README.md`**. This event's lists are already
in git, so you don't need it for the move.

---

*That's the whole thing, Joe. Clone, four commands, done. — Claude*
