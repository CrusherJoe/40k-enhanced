#!/usr/bin/env python3
"""Build the interactive matchup-dossier Artifact (self-contained HTML) from the generated dossier
markdown. Parses reports/dossier-<list>.md for each list, embeds the data, and writes a single page:
list selector -> matchup map (status cards) -> click a card for the full runbook. Framed for LOCKED-list
tournament play (runbooks are the in-event tool; list-building notes are for between events).

  python3 tools/make_dossier_artifact.py knights custodes   # -> reports/dossier.html
"""
import re, json, sys, os

REPORTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
READS = r"FAVOURED|EVEN / GRINDY|ATTRITION-NEGATIVE|HARD"


def parse(list_key):
    t = open(os.path.join(REPORTS, f"dossier-{list_key}.md")).read()
    name = re.search(r"# TOURNAMENT DOSSIER — (.+)", t).group(1).strip()
    tap = t.split("# MATCHUP MAP")[0].split("\n", 2)[2].strip()
    mapsec = t.split("# MATCHUP MAP")[1].split("# RUNBOOKS")[0]
    rows = [dict(opp=m.group(1), arch=m.group(2), read=m.group(3), posture=m.group(4), threat=m.group(5).strip())
            for m in re.finditer(rf"^\s{{2}}(\w+) \((.+?)\)\s{{2,}}({READS})\s+(\w+)\s+(.+?)\s*$", mapsec, re.M)]
    rbsec = t.split("# RUNBOOKS")[1].split("# LIST-BUILDING")[0] if "# LIST-BUILDING" in t else t.split("# RUNBOOKS")[1]
    books = re.findall(r"```\n(.*?)\n```", rbsec, re.S)
    for i, r in enumerate(rows):
        r["runbook"] = books[i].strip() if i < len(books) else ""
    fx = re.search(r"# LIST-BUILDING.*?```\n(.*?)\n```", t, re.S) or re.search(r"# LIST FIXES.*?```\n(.*?)\n```", t, re.S)
    return dict(name=name, tapestry=tap, rows=rows, fixes=fx.group(1).strip() if fx else "")


TEMPLATE = r'''<title>Tactical Dossier — %(titles)s</title>
<div id="app"></div>
<style>
:root{--bg:#efece4;--panel:#f7f5ef;--ink:#20242b;--ink-soft:#5a5f68;--line:#d8d3c6;--brass:#a5771f;--brass-bright:#c69a3a;
--shadow:0 1px 3px rgba(40,34,20,.10);--fav:#3f7d57;--even:#4173a0;--attr:#a9791f;--hard:#a53c31;
--mono:ui-monospace,"SF Mono","DejaVu Sans Mono",Menlo,Consolas,monospace;--disp:"Arial Narrow","Helvetica Neue Condensed",Arial,sans-serif;
--body:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;}
@media (prefers-color-scheme:dark){:root{--bg:#15181d;--panel:#1d2128;--ink:#e6e3da;--ink-soft:#9aa0aa;--line:#2e343d;--brass:#c69a3a;--brass-bright:#e0be6a;--shadow:0 1px 3px rgba(0,0,0,.4);--fav:#5aa876;--even:#6398cc;--attr:#d0a13e;--hard:#cf5a4c;}}
:root[data-theme="dark"]{--bg:#15181d;--panel:#1d2128;--ink:#e6e3da;--ink-soft:#9aa0aa;--line:#2e343d;--brass:#c69a3a;--brass-bright:#e0be6a;--shadow:0 1px 3px rgba(0,0,0,.4);--fav:#5aa876;--even:#6398cc;--attr:#d0a13e;--hard:#cf5a4c;}
:root[data-theme="light"]{--bg:#efece4;--panel:#f7f5ef;--ink:#20242b;--ink-soft:#5a5f68;--line:#d8d3c6;--brass:#a5771f;--brass-bright:#c69a3a;--shadow:0 1px 3px rgba(40,34,20,.10);--fav:#3f7d57;--even:#4173a0;--attr:#a9791f;--hard:#a53c31;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:28px 20px 64px}
header.top{display:flex;flex-wrap:wrap;align-items:flex-end;gap:16px;justify-content:space-between;border-bottom:2px solid var(--brass);padding-bottom:14px;margin-bottom:8px}
.eyebrow{font-family:var(--disp);text-transform:uppercase;letter-spacing:.28em;font-size:12px;color:var(--brass);font-weight:700}
h1{font-family:var(--disp);text-transform:uppercase;letter-spacing:.02em;font-weight:700;font-size:clamp(26px,4.4vw,40px);margin:2px 0 0;text-wrap:balance;line-height:1.02}
.sel{display:flex;gap:6px;background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:4px}
.sel button{font-family:var(--disp);text-transform:uppercase;letter-spacing:.08em;font-weight:700;font-size:13px;background:transparent;color:var(--ink-soft);border:0;padding:8px 14px;border-radius:6px;cursor:pointer}
.sel button.on{background:var(--brass);color:#1a1206}
.sub{color:var(--ink-soft);font-size:13.5px;max-width:66ch;margin:14px 0 6px}
.howto{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--brass);border-radius:7px;padding:11px 15px;font-size:13px;color:var(--ink-soft);margin:12px 0 26px}
.howto b{color:var(--ink)}
h2.sec{font-family:var(--disp);text-transform:uppercase;letter-spacing:.16em;font-size:15px;color:var(--ink);margin:30px 0 12px;display:flex;align-items:center;gap:10px}
h2.sec::after{content:"";flex:1;height:1px;background:var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(214px,1fr));gap:11px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:13px 14px 12px;cursor:pointer;position:relative;overflow:hidden;transition:transform .08s,border-color .12s;border-left:4px solid var(--stripe)}
.card:hover{transform:translateY(-2px);border-color:var(--brass)}
.card.active{border-color:var(--brass);box-shadow:0 0 0 1px var(--brass) inset}
.card:focus-visible{outline:2px solid var(--brass-bright);outline-offset:2px}
.card .opp{font-family:var(--disp);text-transform:uppercase;letter-spacing:.03em;font-weight:700;font-size:19px;line-height:1.05}
.card .arch{font-size:11px;color:var(--ink-soft);text-transform:uppercase;letter-spacing:.1em;margin-top:2px}
.pill{display:inline-block;font-family:var(--disp);text-transform:uppercase;letter-spacing:.07em;font-weight:700;font-size:11px;color:#fff;padding:2.5px 9px;border-radius:11px;margin:9px 0 7px;background:var(--stripe)}
.card .meta{font-size:12px;color:var(--ink-soft);display:flex;flex-direction:column;gap:2px}
.card .meta b{color:var(--ink);font-weight:600}
.read-FAV{--stripe:var(--fav)}.read-EVE{--stripe:var(--even)}.read-ATT{--stripe:var(--attr)}.read-HAR{--stripe:var(--hard)}
#detail{margin-top:22px;background:var(--panel);border:1px solid var(--line);border-radius:11px;border-top:4px solid var(--stripe,var(--brass));box-shadow:var(--shadow);padding:0;overflow:hidden;scroll-margin-top:14px}
.rb-head{padding:16px 20px 4px}
.rb-head .who{font-family:var(--disp);text-transform:uppercase;letter-spacing:.03em;font-weight:700;font-size:22px;line-height:1.05}
.rb-head .mission{font-size:12px;color:var(--ink-soft);margin-top:3px}
.rb-body{padding:6px 20px 20px}
.rb-body pre{font-family:var(--mono);font-size:12.5px;line-height:1.62;white-space:pre-wrap;margin:0;overflow-x:auto;color:var(--ink)}
.rb-body .lbl{color:var(--brass);font-weight:700;font-family:var(--disp);letter-spacing:.05em}
.rb-body .rd{color:var(--stripe,var(--brass));font-weight:700}
.rb-body .trap{color:var(--hard);font-weight:700}
details{margin-top:26px;background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:2px 16px}
details>summary{font-family:var(--disp);text-transform:uppercase;letter-spacing:.12em;font-weight:700;font-size:14px;cursor:pointer;padding:12px 0;color:var(--ink)}
details pre{font-family:var(--mono);font-size:12px;line-height:1.6;white-space:pre-wrap;overflow-x:auto;color:var(--ink-soft);padding-bottom:14px;margin:0}
.foot{margin-top:34px;padding-top:14px;border-top:1px solid var(--line);font-size:11.5px;color:var(--ink-soft)}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:2px 0 4px;font-size:11.5px;color:var(--ink-soft)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{width:11px;height:11px;border-radius:3px;display:inline-block}
@media (max-width:560px){.card .opp{font-size:17px}}
@media (prefers-reduced-motion:reduce){.card{transition:none}}
</style>
<script>
const DATA=%(data)s, LISTS=%(lists)s;
const READKEY=r=>r.startsWith("FAV")?"FAV":r.startsWith("EVEN")?"EVE":r.startsWith("ATTR")?"ATT":"HAR";
const READLBL=r=>r.startsWith("FAV")?"Favoured":r.startsWith("EVEN")?"Even / grindy":r.startsWith("ATTR")?"Attrition-negative":"Hard";
let cur=LISTS[0].key, sel=0;
function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function fmtRunbook(txt){return esc(txt).split("\n").map(l=>{
  if(/^(READ|WIN CONDITION|POSTURE|DEPLOYMENT):/.test(l)){const i=l.indexOf(":");const cls=l.startsWith("READ")?"rd":"lbl";return '<span class="lbl">'+l.slice(0,i)+':</span><span class="'+cls+'">'+l.slice(i+1)+'</span>';}
  if(/^(PRIORITY KILLS|PLAY AROUND|YOUR WORKHORSES|YOUR LIABILITIES|KEY STRATAGEMS|BOARD CONTROL)/.test(l)){const i=l.indexOf(":")>=0?l.indexOf(":"):l.length;return '<span class="lbl">'+l.slice(0,i)+'</span>'+l.slice(i);}
  if(/^THE TRAP:/.test(l)){return '<span class="lbl">THE TRAP:</span><span class="trap">'+l.slice(9)+'</span>';}
  return l;}).join("\n");}
function render(){
  const d=DATA[cur], rows=d.rows;
  const cards=rows.map((r,i)=>{const rk=READKEY(r.read);return `<div class="card read-${rk} ${i===sel?'active':''}" tabindex="0" role="button" data-i="${i}" aria-label="${esc(r.opp)}, ${READLBL(r.read)}"><div class="opp">${esc(r.opp.replace(/_/g,' '))}</div><div class="arch">${esc(r.arch)}</div><span class="pill">${READLBL(r.read)}</span><div class="meta"><span>Posture: <b>${esc(r.posture)}</b></span><span>Biggest threat: <b>${esc(r.threat)}</b></span></div></div>`;}).join("");
  const r=rows[sel], rk=READKEY(r.read), L=r.runbook.split("\n");
  const who=esc(L[0].replace(/^RUNBOOK — /,"")), mission=esc((L[1]||"").trim()), rest=fmtRunbook(L.slice(2).join("\n").trim());
  const fixes=d.fixes?`<h2 class="sec">List-Building Notes</h2><div class="howto" style="border-left-color:var(--ink-soft)">Between events only — your list is LOCKED at the tournament. Use this when deciding what to bring.</div><details><summary>Optimiser: tested swaps</summary><pre>${esc(d.fixes)}</pre></details>`:"";
  const btns=LISTS.length>1?`<div class="sel" role="tablist">`+LISTS.map(l=>`<button class="${cur===l.key?'on':''}" data-list="${l.key}">${esc(l.label)}</button>`).join("")+`</div>`:"";
  document.getElementById("app").innerHTML=`<div class="wrap">
    <header class="top"><div><div class="eyebrow">Tactical Dossier</div><h1>${esc(d.name)}</h1></div>${btns}</header>
    <p class="sub">How your <b>locked tournament list</b> maps into the current meta — a positional simulation (thousands of dice-resolved games per matchup). The numbers describe the <b>dynamics</b>, not a win-rate prediction.</p>
    <div class="howto"><b>In-event tool:</b> tap any matchup for its RUNBOOK — how to pilot THIS list against it: who to kill first, what you <b>can't</b> remove (don't feed it), what to protect, your posture &amp; deployment, and the trap that loses the game. The map is your at-a-glance cheat sheet.</div>
    <h2 class="sec">Matchup Map</h2>
    <div class="legend"><span><i style="background:var(--fav)"></i>Favoured</span><span><i style="background:var(--even)"></i>Even / grindy</span><span><i style="background:var(--attr)"></i>Attrition-negative</span><span><i style="background:var(--hard)"></i>Hard</span></div>
    <div class="grid">${cards}</div>
    <div id="detail" class="read-${rk}"><div class="rb-head"><div class="who">${who}</div><div class="mission">${mission}</div></div><div class="rb-body"><pre>${rest}</pre></div></div>
    ${fixes}
    <div class="foot">wh.sim positional simulator · mechanistic matchup analysis, not a win-rate oracle · ${rows.length} archetypes.</div></div>`;
  document.querySelectorAll(".card").forEach(c=>{const go=()=>{sel=+c.dataset.i;render();document.getElementById("detail").scrollIntoView({behavior:"smooth",block:"start"});};c.onclick=go;c.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();go();}};});
  document.querySelectorAll(".sel button").forEach(b=>b.onclick=()=>{cur=b.dataset.list;sel=0;render();});
}
render();
</script>'''

LABELS = {"knights": "Imperial Knights", "custodes": "Custodes"}


def main(keys, combined=False):
    if combined:                                    # legacy: one page, list selector
        data = {k: parse(k) for k in keys}
        lists = [dict(key=k, label=LABELS.get(k, data[k]["name"].split("—")[0].strip())) for k in keys]
        html = TEMPLATE % dict(data=json.dumps(data), lists=json.dumps(lists),
                               titles=" & ".join(LABELS.get(k, k).split()[-1] for k in keys))
        open(os.path.join(REPORTS, "dossier.html"), "w").write(html)
        print("wrote dossier.html")
        return
    for k in keys:                                  # one STANDALONE page per list (give each teammate theirs)
        d = parse(k)
        lists = [dict(key=k, label=LABELS.get(k, d["name"].split("—")[0].strip()))]
        html = TEMPLATE % dict(data=json.dumps({k: d}), lists=json.dumps(lists),
                               titles=LABELS.get(k, d["name"].split("—")[0].strip()))
        out = os.path.join(REPORTS, f"dossier-{k}.html")
        open(out, "w").write(html)
        print("wrote", out, len(html), "bytes")


if __name__ == "__main__":
    args = sys.argv[1:] or ["knights", "custodes"]
    main([a for a in args if a != "--combined"], combined="--combined" in args)
