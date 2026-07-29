#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_fieldguide.py — render the field dossier as a self-contained HTML field guide (Artifact).

Merges data/bcp/<event>-archetypes.json (archetypes, players, verdict, how-to-play) with the sim
reads + runbooks parsed from reports/<me>-field-dossier.md, and writes a single-file interactive
page: ENEMY IDENT search (player name -> archetype card) + a THREAT MAP (archetypes by prevalence,
coloured by verdict, with a sim-vs-verdict agreement glyph) + expandable runbooks & player rosters.

  python3 tools/make_fieldguide.py            # -> reports/death_rnr-fieldguide.html
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(ROOT, "data", "bcp", "lso2026-archetypes.json")
DOSSIER = os.path.join(ROOT, "reports", "death_rnr-field-dossier.md")
OUT = os.path.join(ROOT, "reports", "death_rnr-fieldguide.html")


def parse_dossier(path):
    """-> ({key: {sim, margin}}, {key: runbook_text}, me_name, disposition, meta)."""
    t = open(path, encoding="utf-8").read()
    me = re.search(r"# Field Dossier — (.+)", t).group(1).strip()
    disp = (re.search(r"disposition:\s*\*\*(.+?)\*\*", t) or [None, "?"])[1]
    meta = (re.search(r"vs the (.+?)\*", t) or [None, ""])[1].strip().rstrip(".")
    sim = {}
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*([A-Z\-]+)\s*\|\s*([+\-][\d.]+|—)\s*\|$",
                         t, re.M):
        key = m.group(2).strip()
        sim[key] = {"sim": m.group(4).strip(),
                    "margin": None if m.group(5) == "—" else float(m.group(5))}
    books = {}
    for m in re.finditer(r"^### (.+?)\s+·.*?\n(?:\n\*\*How to play:\*\*.*?\n)?\n```\n(.*?)\n```",
                         t, re.S | re.M):
        books[m.group(1).strip()] = m.group(2).strip()
    return sim, books, me, disp, meta


def bucket(verdict, sim, margin):
    """Trust bucket from the hand-verdict + the (directional) sim read. Colour is by verdict;
    this drives the sim-agreement glyph + filter grouping."""
    v = verdict.upper()
    good = v.startswith(("FAVOURABLE", "MIRROR"))
    bad = v.startswith(("UNFAVOURABLE", "HARD"))
    simneg = (sim in ("HARD", "ATTRITION-NEGATIVE")) or (margin is not None and margin < -0.1)
    simpos = (sim in ("FAVOURED",)) or (margin is not None and margin > 0.3)
    if bad and simneg:
        return "confirmed-hard", "✓", "sim concurs — a real problem table"
    if bad and simpos:
        return "trust-verdict", "⚠", "sim is blind here (it over-credits you) — trust the verdict"
    if not bad and simneg:
        return "sim-flags", "▲", "sim flags this WORSE than the verdict — respect it"
    if good and simpos:
        return "confirmed-good", "✓", "sim concurs — a favourable table"
    return "coinflip", "◦", "play it on the notes, not the sim"


VCLASS = {"FAVOURABLE": "fav", "MIRROR": "mirror", "COIN-FLIP": "coin",
          "UNFAVOURABLE": "unfav", "HARD": "hard"}


def _verdict_tier(verdict):
    """(display label, css class) from the LEADING verdict keyword — verdicts can carry a
    qualifier like 'COIN-FLIP → HARD (…)' or 'UNFAVOURABLE → directional', so match the prefix."""
    v = (verdict or "").upper().strip()
    for kw in ("FAVOURABLE", "MIRROR", "COIN-FLIP", "UNFAVOURABLE", "HARD"):
        if v.startswith(kw):
            return kw, VCLASS[kw]
    return "UNSCORED", "unscored"


def build():
    rec = json.load(open(ARCH, encoding="utf-8"))
    sim, books, me, disp, meta = parse_dossier(DOSSIER)
    arches = []
    for key, a in rec["archetypes"].items():
        if a["size"] < 1:
            continue
        s = sim.get(key, {})
        vshort, vcls = _verdict_tier(a["verdict"])       # leading keyword (handles "COIN-FLIP → HARD")
        bkey, glyph, gtip = bucket(a["verdict"] or "", s.get("sim", "—"), s.get("margin"))
        arches.append({
            "key": key, "faction": a["faction"], "det": a["detachment"], "n": a["size"],
            "verdict": a["verdict"] or "", "vshort": vshort, "vclass": vcls,
            "play": a["play"] or "", "sim": s.get("sim", "—"), "margin": s.get("margin"),
            "bucket": bkey, "glyph": glyph, "gtip": gtip,
            "runbook": books.get(key, ""),
            "disp": sorted(a["dispositions"].items(), key=lambda x: -x[1]),
            "players": sorted([{"name": p["player"], "disp": p["disposition"], "url": p["list_url"]}
                               for p in a["players"]], key=lambda x: x["name"]),
        })
    arches.sort(key=lambda x: (-x["n"], x["key"]))
    pindex = [{"name": n, "key": k} for n, k in sorted(rec["player_index"].items())]
    payload = {"me": me, "disp": disp, "meta": meta, "n_lists": rec["n_lists"],
               "n_arch": rec["n_archetypes"], "arches": arches, "players": pindex}
    open(OUT, "w", encoding="utf-8").write(TEMPLATE.replace("/*DATA*/", json.dumps(payload)))
    print(f"# wrote {OUT}  ({len(arches)} archetypes, {len(pindex)} players, {len(books)} runbooks)",
          file=sys.stderr)


TEMPLATE = r"""<title>Field Manual — LSO 2026</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
  --bg:#14171c; --panel:#1b1f26; --panel-2:#20252e; --ink:#e7e4db; --soft:#99a0ac; --faint:#6b7280;
  --line:#2b313b; --brass:#c69a3a; --brass-hi:#e6c66f;
  --fav:#5aa876; --coin:#6a9bd0; --unfav:#d3a63f; --hard:#d15a4c; --mirror:#9aa4b2; --unscored:#5f6772;
  --mono:ui-monospace,"SF Mono","DejaVu Sans Mono",Menlo,Consolas,monospace;
  --disp:"Arial Narrow","Helvetica Neue Condensed","Roboto Condensed",Arial,sans-serif;
  --body:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --sh:0 2px 10px rgba(0,0,0,.35);
}
@media (prefers-color-scheme:light){:root{
  --bg:#e9e5db; --panel:#f4f1ea; --panel-2:#efeae0; --ink:#22262d; --soft:#5a6069; --faint:#8b909a;
  --line:#d6cfc0; --brass:#9a6f1c; --brass-hi:#b98d2e;
  --fav:#3f7d57; --coin:#3f6fa0; --unfav:#9a761f; --hard:#a83e30; --mirror:#6a727e; --unscored:#8b909a;
  --sh:0 1px 4px rgba(60,50,30,.14);
}}
:root[data-theme="light"]{
  --bg:#e9e5db; --panel:#f4f1ea; --panel-2:#efeae0; --ink:#22262d; --soft:#5a6069; --faint:#8b909a;
  --line:#d6cfc0; --brass:#9a6f1c; --brass-hi:#b98d2e;
  --fav:#3f7d57; --coin:#3f6fa0; --unfav:#9a761f; --hard:#a83e30; --mirror:#6a727e; --unscored:#8b909a;
  --sh:0 1px 4px rgba(60,50,30,.14);
}
:root[data-theme="dark"]{
  --bg:#14171c; --panel:#1b1f26; --panel-2:#20252e; --ink:#e7e4db; --soft:#99a0ac; --faint:#6b7280;
  --line:#2b313b; --brass:#c69a3a; --brass-hi:#e6c66f;
  --fav:#5aa876; --coin:#6a9bd0; --unfav:#d3a63f; --hard:#d15a4c; --mirror:#9aa4b2; --unscored:#5f6772;
  --sh:0 2px 10px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.5;
  -webkit-text-size-adjust:100%;}
.wrap{max-width:900px;margin:0 auto;padding:0 18px 80px;}
a{color:var(--brass);}
/* --- header --- */
header{position:sticky;top:0;z-index:20;background:linear-gradient(var(--bg),var(--bg) 78%,transparent);
  padding-top:20px;}
.eyebrow{font:600 11px/1 var(--mono);letter-spacing:.28em;text-transform:uppercase;color:var(--brass);
  display:flex;align-items:center;gap:10px;}
.eyebrow::before{content:"";width:22px;height:2px;background:var(--brass);}
h1{font-family:var(--disp);font-weight:800;letter-spacing:.01em;text-transform:uppercase;
  font-size:clamp(26px,5vw,42px);line-height:.98;margin:.28em 0 .12em;text-wrap:balance;}
.sub{color:var(--soft);font-size:14px;margin-bottom:2px;}
.sub b{color:var(--ink);font-weight:600;}
.disp-chip{display:inline-block;font:600 11px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;
  color:var(--brass-hi);border:1px solid var(--brass);border-radius:3px;padding:4px 7px;margin-left:2px;}
.toggle{position:absolute;top:20px;right:18px;font:600 10px/1 var(--mono);letter-spacing:.14em;
  background:var(--panel);color:var(--soft);border:1px solid var(--line);border-radius:4px;
  padding:7px 9px;cursor:pointer;text-transform:uppercase;}
.toggle:hover{color:var(--brass-hi);border-color:var(--brass);}
/* --- ident search --- */
.ident{background:var(--panel);border:1px solid var(--line);border-top:2px solid var(--brass);
  border-radius:8px;padding:16px 16px 14px;margin:16px 0 8px;box-shadow:var(--sh);}
.ident label{font:600 11px/1 var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--soft);}
.ident input{width:100%;margin-top:9px;background:var(--bg);border:1px solid var(--line);color:var(--ink);
  font:500 17px/1.2 var(--body);padding:12px 13px;border-radius:6px;}
.ident input:focus{outline:2px solid var(--brass);outline-offset:1px;border-color:var(--brass);}
#identOut{margin-top:12px;display:none;}
#identOut.on{display:block;}
.idhit{font:12px/1.4 var(--mono);color:var(--soft);padding:6px 0;border-top:1px dashed var(--line);cursor:pointer;}
.idhit:hover{color:var(--brass-hi);}
.idhit b{color:var(--ink);font-weight:600;}
/* --- filter bar --- */
.filters{display:flex;flex-wrap:wrap;gap:6px;margin:18px 0 12px;align-items:center;}
.flabel{font:600 10px/1 var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--faint);margin-right:4px;}
.chip{font:600 11px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:6px 10px;border-radius:20px;
  border:1px solid var(--line);background:var(--panel);color:var(--soft);cursor:pointer;}
.chip[aria-pressed="true"]{color:var(--bg);background:var(--brass);border-color:var(--brass);}
.chip .dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle;}
/* --- threat map --- */
.count{font:11px/1 var(--mono);color:var(--faint);letter-spacing:.1em;text-transform:uppercase;margin:6px 2px 10px;}
.row{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--vc);border-radius:7px;
  margin-bottom:8px;box-shadow:var(--sh);overflow:hidden;}
.rhead{display:grid;grid-template-columns:44px 1fr auto;gap:12px;align-items:center;padding:13px 15px;cursor:pointer;}
.rhead:hover{background:var(--panel-2);}
.pop{font-family:var(--disp);font-weight:800;font-size:26px;line-height:1;color:var(--ink);text-align:center;
  font-variant-numeric:tabular-nums;}
.pop small{display:block;font:500 8px/1 var(--mono);letter-spacing:.14em;color:var(--faint);margin-top:3px;}
.arch{font-family:var(--disp);font-weight:700;text-transform:uppercase;letter-spacing:.02em;font-size:18px;
  line-height:1.05;color:var(--ink);}
.det{font:12px/1.3 var(--mono);color:var(--soft);margin-top:2px;}
.rmeta{display:flex;align-items:center;gap:9px;justify-self:end;}
.pill{font:700 10px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;padding:5px 8px;border-radius:4px;
  color:var(--bg);background:var(--vc);white-space:nowrap;}
.glyph{font-size:15px;width:20px;text-align:center;color:var(--soft);}
.chev{color:var(--faint);font-size:13px;transition:transform .18s;}
.row.open .chev{transform:rotate(90deg);}
.body{display:none;padding:2px 16px 17px;border-top:1px solid var(--line);}
.row.open .body{display:block;}
.simline{font:12px/1.5 var(--mono);color:var(--soft);margin:12px 0;padding:9px 11px;background:var(--bg);
  border-radius:5px;border:1px solid var(--line);}
.simline .g{color:var(--ink);}
.play{margin:12px 0;}
.play h4,.rb h4{font:600 10px/1 var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--brass);
  margin:0 0 6px;}
.play p{margin:0;font-size:14.5px;color:var(--ink);}
.rb pre{font:12px/1.5 var(--mono);white-space:pre-wrap;background:var(--bg);border:1px solid var(--line);
  border-radius:6px;padding:12px;color:var(--soft);overflow-x:auto;margin:0;}
.rb pre b{color:var(--ink);}
.rb .norb{font-size:12.5px;color:var(--soft);font-style:italic;margin:0;}
.roster{margin-top:14px;}
.roster h4{font:600 10px/1 var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--faint);margin:0 0 7px;}
.pilots{display:flex;flex-wrap:wrap;gap:6px;}
.pilot{font:12px/1 var(--mono);color:var(--soft);background:var(--bg);border:1px solid var(--line);
  border-radius:4px;padding:5px 8px;}
.pilot a{color:inherit;text-decoration:none;}.pilot a:hover{color:var(--brass-hi);}
.foot{margin-top:26px;font:11px/1.6 var(--mono);color:var(--faint);border-top:1px solid var(--line);padding-top:14px;}
mark{background:var(--brass);color:var(--bg);border-radius:2px;padding:0 2px;}
@media (max-width:560px){.rhead{grid-template-columns:38px 1fr;}.rmeta{grid-column:1/-1;justify-self:start;padding-left:50px;}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;}}
</style>

<div class="wrap">
<header>
  <button class="toggle" id="tg" aria-label="Toggle theme">◐ Theme</button>
  <div class="eyebrow">Imperial Knights · Field Manual</div>
  <h1 id="me"></h1>
  <div class="sub" id="brief"></div>
</header>

<section class="ident">
  <label for="q">▸ Enemy pilot ident</label>
  <input id="q" type="text" autocomplete="off" spellcheck="false"
    placeholder="Type an opponent's name (e.g. Torres, Colavito)…">
  <div id="identOut"></div>
</section>

<div class="filters" id="filters">
  <span class="flabel">Threat map</span>
</div>
<div class="count" id="count"></div>
<div id="map"></div>

<div class="foot" id="foot"></div>
</div>

<script>
const D = /*DATA*/;
const VC = {fav:'--fav',coin:'--coin',unfav:'--unfav',hard:'--hard',mirror:'--mirror',unscored:'--unscored'};
// Filter chips = VERDICT tiers (so a chip's dot colour matches the rows it shows). The one
// cross-axis chip, "Sim disagrees", is brass (a different axis) + surfaces the ⚠/▲ rows.
const CHIPS = [
  ['all','All',null],
  ['fav','Favourable','--fav'],
  ['coin','Coin-flip','--coin'],
  ['unfav','Unfavourable','--unfav'],
  ['hard','Hard','--hard'],
  ['mirror','Mirror','--mirror'],
  ['disagree','⚠ Sim disagrees','--brass'],
];
function match(a,k){
  if(k==='all') return true;
  if(k==='disagree') return a.bucket==='trust-verdict'||a.bucket==='sim-flags';
  return a.vclass===k;
}
const esc = s => (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const boldRB = s => esc(s).replace(/^(READ:|WIN CONDITION:|POSTURE:|DEPLOYMENT:|THE TRAP:|PRIORITY KILLS.*?:|PLAY AROUND.*?:|YOUR WORKHORSES.*?:|YOUR LIABILITIES.*?:|BOARD CONTROL.*?:)/gm,'<b>$1</b>');
let filter='all';

// header
document.getElementById('me').textContent = D.me;
document.getElementById('brief').innerHTML =
  `vs the <b>${esc(D.meta)}</b> · ${D.n_lists} lists / ${D.n_arch} archetypes · your disposition `+
  `<span class="disp-chip">${esc(D.disp)}</span>`;
document.getElementById('foot').innerHTML =
  `Verdicts + how-to-play are hand-set from the Knights seat and are the plan. The <b>sim</b> read is the `+
  `positional simulator — <b>directional only</b>, it over-credits you in melee / vs reanimation & hordes, `+
  `so a ⚠ means trust the verdict. Board = your avg objective margin R4–5. Field: ${esc(D.meta)}.`;

// filters
const fbar=document.getElementById('filters');
CHIPS.forEach(([k,label,vc])=>{
  const n = D.arches.filter(a=>match(a,k)).length;
  if(k!=='all' && n===0) return;
  const b=document.createElement('button');
  b.className='chip'; b.setAttribute('aria-pressed', k==='all'); b.dataset.k=k;
  b.innerHTML = (vc?`<span class="dot" style="background:var(${vc})"></span>`:'')+`${label} <span style="opacity:.6">${n}</span>`;
  b.onclick=()=>{filter=k; [...fbar.querySelectorAll('.chip')].forEach(c=>c.setAttribute('aria-pressed',c.dataset.k===k)); render();};
  fbar.appendChild(b);
});

function card(a){
  const vc=VC[a.vclass]||'--unscored';
  const mg = a.margin==null?'':`<span title="board margin R4-5">${a.margin>0?'+':''}${a.margin.toFixed(2)}</span>`;
  const dispStr = a.disp.map(([d,n])=>`${d} ${n}`).join(' · ');
  const rb = a.runbook
    ? `<div class="rb"><h4>Runbook — sim vs a real list</h4><pre>${boldRB(a.runbook)}</pre></div>`
    : `<div class="rb"><h4>Runbook</h4><p class="norb">No sim runbook — this list uses an export format the parser can't read into the engine. The verdict + how-to-play above are the plan.</p></div>`;
  const pilots = a.players.map(p=>`<span class="pilot"><a href="${p.url}" target="_blank" rel="noopener">${esc(p.name)}</a></span>`).join('');
  return `<div class="row" style="--vc:var(${vc})" data-bucket="${a.bucket}" data-key="${esc(a.key.toLowerCase())}">
    <div class="rhead">
      <div class="pop">${a.n}<small>pilots</small></div>
      <div><div class="arch">${esc(a.det)}</div><div class="det">${esc(a.faction)} · ${esc(dispStr)}</div></div>
      <div class="rmeta">
        <span class="glyph" title="${esc(a.gtip)}">${a.glyph}</span>
        <span class="pill">${esc(a.vshort)}</span>
        <span class="chev">▶</span>
      </div>
    </div>
    <div class="body">
      <div class="simline"><span class="g">SIM:</span> ${esc(a.sim)} ${mg} &nbsp;·&nbsp; ${esc(a.gtip)}</div>
      ${a.play?`<div class="play"><h4>How to play</h4><p>${esc(a.play)}</p></div>`:''}
      ${rb}
      <div class="roster"><h4>Pilots running this (${a.players.length})</h4><div class="pilots">${pilots}</div></div>
    </div></div>`;
}

function render(){
  const list = D.arches.filter(a=>match(a,filter));
  document.getElementById('map').innerHTML = list.map(card).join('');
  const nl = list.reduce((s,a)=>s+a.n,0);
  document.getElementById('count').textContent = `${list.length} archetypes · ${nl} of ${D.n_lists} lists`;
  document.querySelectorAll('.rhead').forEach(h=>h.onclick=()=>h.parentElement.classList.toggle('open'));
}
render();

// ident search
const q=document.getElementById('q'), out=document.getElementById('identOut');
q.addEventListener('input',()=>{
  const v=q.value.trim().toLowerCase();
  if(v.length<2){out.className='';out.innerHTML='';return;}
  const hits=D.players.filter(p=>p.name.toLowerCase().includes(v)).slice(0,8);
  out.className='on';
  if(!hits.length){out.innerHTML=`<div class="idhit">no pilot matching “${esc(q.value)}” in the field</div>`;return;}
  out.innerHTML=hits.map(p=>{
    const a=D.arches.find(x=>x.key===p.key)||{};
    const vc=VC[a.vclass]||'--unscored';
    return `<div class="idhit" data-key="${esc(p.key.toLowerCase())}"><b>${esc(p.name)}</b> → `+
      `<span style="color:var(${vc})">${esc(a.vshort||'?')}</span> · ${esc(a.det||p.key)} `+
      `<span style="opacity:.6">[${esc((a.play||'').slice(0,70))}${(a.play||'').length>70?'…':''}]</span></div>`;
  }).join('');
  out.querySelectorAll('.idhit[data-key]').forEach(h=>h.onclick=()=>{
    filter='all'; [...fbar.querySelectorAll('.chip')].forEach(c=>c.setAttribute('aria-pressed',c.dataset.k==='all')); render();
    const row=[...document.querySelectorAll('.row')].find(r=>r.dataset.key===h.dataset.key);
    if(row){row.classList.add('open');row.scrollIntoView({behavior:'smooth',block:'center'});
      row.style.transition='box-shadow .3s';row.style.boxShadow='0 0 0 2px var(--brass)';
      setTimeout(()=>row.style.boxShadow='',1400);}
  });
});

// theme toggle
const root=document.documentElement, tg=document.getElementById('tg');
tg.onclick=()=>{const cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  root.setAttribute('data-theme',cur==='dark'?'light':'dark');};
</script>
"""

if __name__ == "__main__":
    build()
