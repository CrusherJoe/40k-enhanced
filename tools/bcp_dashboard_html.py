#!/usr/bin/env python3
"""bcp_dashboard_html.py — render the weekly-meta feed (from bcp_dashboard.build_data) into a single
self-contained, theme-aware HTML dashboard. No external assets (works offline / publishable as an Artifact)."""
import json

_TMPL = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>40K 11E Meta Tracker — Weekly Win Rates &amp; Field Share</title>
<style>
:root{
  --bg:#f5f6f8; --surface:#ffffff; --surface2:#eef0f4; --border:#e2e5ec; --line:#d8dbe3;
  --ink:#1a1d26; --muted:#727888; --faint:#9aa0b0;
  --accent:#b07d17; --accent-ink:#7a5610;
  --good:#1f9d6b; --mid:#8b91a3; --bad:#d64f47;
  --grid:#eceef3;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#101219; --surface:#1a1d26; --surface2:#20242f; --border:#2a2f3d; --line:#333a4b;
  --ink:#e8eaf0; --muted:#8b91a3; --faint:#5c6374;
  --accent:#e0a53a; --accent-ink:#e8b855;
  --good:#43c08e; --mid:#7f8698; --bad:#e56b62;
  --grid:#232833;
}}
:root[data-theme="light"]{
  --bg:#f5f6f8; --surface:#ffffff; --surface2:#eef0f4; --border:#e2e5ec; --line:#d8dbe3;
  --ink:#1a1d26; --muted:#727888; --faint:#9aa0b0;
  --accent:#b07d17; --accent-ink:#7a5610; --good:#1f9d6b; --mid:#8b91a3; --bad:#d64f47; --grid:#eceef3;
}
:root[data-theme="dark"]{
  --bg:#101219; --surface:#1a1d26; --surface2:#20242f; --border:#2a2f3d; --line:#333a4b;
  --ink:#e8eaf0; --muted:#8b91a3; --faint:#5c6374;
  --accent:#e0a53a; --accent-ink:#e8b855; --good:#43c08e; --mid:#7f8698; --bad:#e56b62; --grid:#232833;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);
  font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:28px 20px 64px}
.num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1}
.eyebrow{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600}

header .eyebrow{color:var(--accent-ink)}
h1{font-size:27px;line-height:1.12;margin:6px 0 4px;font-weight:750;letter-spacing:-.015em;text-wrap:balance}
.sub{color:var(--muted);margin:0;max-width:60ch}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px}
.chip{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:8px 13px;min-width:78px}
.chip b{display:block;font-size:20px;font-weight:700;letter-spacing:-.01em}
.chip span{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.method{font-size:12.5px;color:var(--muted);margin-top:12px;border-left:2px solid var(--border);padding-left:12px}
.method code{background:var(--surface2);padding:1px 5px;border-radius:4px;font-size:11.5px}

.controls{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end;margin:26px 0 14px;
  padding-top:20px;border-top:1px solid var(--border)}
.ctl{display:flex;flex-direction:column;gap:6px}
.seg{display:inline-flex;background:var(--surface2);border:1px solid var(--border);border-radius:9px;padding:3px}
.seg button{appearance:none;border:0;background:transparent;color:var(--muted);font:inherit;font-weight:600;
  font-size:13.5px;padding:6px 15px;border-radius:6px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--accent);color:#1a1400;box-shadow:0 1px 2px rgba(0,0,0,.25)}
select{appearance:none;background:var(--surface);color:var(--ink);border:1px solid var(--border);
  border-radius:8px;padding:8px 30px 8px 12px;font:inherit;font-size:14px;cursor:pointer;
  background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);
  background-position:calc(100% - 15px) 55%,calc(100% - 10px) 55%;background-size:5px 5px,5px 5px;background-repeat:no-repeat}
.spacer{flex:1}
.count{font-size:12.5px;color:var(--muted);align-self:center}

.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;overflow:hidden}
.chartcard{padding:18px 18px 10px;margin-bottom:18px}
.chartcard h2,.tablecard h2{font-size:13px;margin:0 0 2px;font-weight:650}
.chartcard .cap{font-size:12px;color:var(--muted);margin:0 0 8px}
.chartwrap{overflow-x:auto}
svg{display:block;width:100%;height:auto;min-width:420px}
.legend{display:flex;flex-wrap:wrap;gap:12px 16px;margin-top:8px}
.legend span{font-size:12px;color:var(--muted);display:inline-flex;align-items:center;gap:6px}
.legend i{width:11px;height:3px;border-radius:2px;display:inline-block}

.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:560px}
th,td{text-align:right;padding:9px 14px;border-bottom:1px solid var(--border);white-space:nowrap}
th{font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:600;
  cursor:pointer;user-select:none;position:sticky;top:0;background:var(--surface)}
th.l,td.l{text-align:left}
th[aria-sort]{color:var(--ink)}
th .ar{opacity:.6;font-size:9px;margin-left:3px}
tbody tr:hover{background:var(--surface2)}
td.rank{color:var(--faint);width:34px}
td.name{font-weight:600}
.share{display:flex;align-items:center;gap:9px;justify-content:flex-end}
.share .bar{height:7px;border-radius:4px;background:var(--accent);opacity:.55;min-width:2px}
.share small{color:var(--muted);width:38px;text-align:right}
.wr{display:flex;align-items:center;gap:9px;justify-content:flex-end}
.wr .track{width:96px;height:8px;border-radius:5px;background:var(--surface2);overflow:hidden;position:relative}
.wr .fill{height:100%;border-radius:5px}
.wr b{width:44px;text-align:right;font-weight:700}
.flag{color:var(--faint);font-size:11px;cursor:help}
.dash{color:var(--faint)}
footer{margin-top:26px;font-size:12px;color:var(--muted);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
@media (max-width:560px){.wrap{padding:20px 14px 48px}h1{font-size:22px}.chip b{font-size:17px}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow">Warhammer 40,000 · 11th Edition · Tournament Meta</div>
    <h1>Weekly Meta Tracker</h1>
    <p class="sub">Win rate and field share by faction, mission disposition, and detachment — from championship
      tournament results worldwide.</p>
    <div class="chips" id="chips"></div>
    <p class="method" id="method"></p>
  </header>

  <div class="controls">
    <div class="ctl">
      <span class="eyebrow">Dimension</span>
      <div class="seg" id="dimseg" role="group" aria-label="Dimension">
        <button data-dim="faction" aria-pressed="true">Faction</button>
        <button data-dim="disposition" aria-pressed="false">Disposition</button>
        <button data-dim="detachment" aria-pressed="false">Detachment</button>
      </div>
    </div>
    <div class="ctl">
      <span class="eyebrow">Week</span>
      <select id="weeksel"></select>
    </div>
    <div class="spacer"></div>
    <div class="count" id="count"></div>
  </div>

  <div class="card chartcard">
    <h2>Win rate over time</h2>
    <p class="cap" id="chartcap"></p>
    <div class="chartwrap"><svg id="chart" viewBox="0 0 720 240" preserveAspectRatio="xMidYMid meet"></svg></div>
    <div class="legend" id="legend"></div>
  </div>

  <div class="card tablecard">
    <div class="tablewrap"><table id="tbl"><thead></thead><tbody></tbody></table></div>
  </div>

  <footer>
    <span>Generated <span id="gen"></span> · source: BestCoastPairings championship results</span>
    <span id="foot-n"></span>
  </footer>
</div>

<script>
const DATA = __DATA__;
const LINE = ["#e0a53a","#4c9be8","#43c08e","#c77dd6","#e56b62","#6fc7c0"];
let dim="faction", week="__ALL__", sortKey="players", sortDir=-1;

const wr = r => r.games ? r.wins/r.games : null;
const pctColor = p => p==null ? "var(--mid)" : p>=0.52 ? "var(--good)" : p<=0.48 ? "var(--bad)" : "var(--mid)";
const esc = s => (s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

const T4=()=>DATA.weeks.slice(-4).map(w=>w.start);   // last up-to-4 meta weeks
function cell(row){                     // resolve a row's stats for the current week filter
  if(week==="__ALL__") return {...row.total};
  const keys = week==="__T4__" ? T4() : [week];
  const o={games:0,wins:0,players:0};
  for(const k of keys){const w=row.byweek[k]; if(w){o.games+=w.games;o.wins+=w.wins;o.players+=w.players;}}
  return o;
}

function initChrome(){
  const s=DATA.summary;
  const chips=[["events",s.events],["games",s.games.toLocaleString()],["weeks",s.weeks],
    ["factions",DATA.faction.filter(r=>r.total.players).length]];
  document.getElementById("chips").innerHTML=chips.map(([k,v])=>`<div class="chip"><b class="num">${v}</b><span>${k}</span></div>`).join("");
  document.getElementById("method").innerHTML=
    `Win rate = decided games, both sides. Field share = players bringing it. Bucketed by <b>meta week (Wed–Tue)</b> `+
    `and event date — matching community trackers — so each week reflects that week's balance. Single-weekend GTs `+
    `(leagues &amp; team events excluded). Faction &amp; disposition come from public rosters; <b>detachment</b> comes `+
    `from army-list text, so it is only as complete as the list corpus — win rates on fewer than ${DATA.low_n} games are flagged as noisy.`;
  document.getElementById("gen").textContent=DATA.generated_utc.replace("T"," ").replace("Z"," UTC");
  const sel=document.getElementById("weeksel");
  const t4=DATA.weeks.length>1?`<option value="__T4__">Last 4 weeks</option>`:"";
  sel.innerHTML=`<option value="__ALL__">All weeks (cumulative)</option>`+t4+
    DATA.weeks.map(w=>`<option value="${w.start}">Week of ${w.label}</option>`).join("");
  document.getElementById("dimseg").addEventListener("click",e=>{
    const b=e.target.closest("button"); if(!b)return;
    dim=b.dataset.dim; [...e.currentTarget.children].forEach(x=>x.setAttribute("aria-pressed",x===b));
    sortKey="players";sortDir=-1; render();
  });
  sel.addEventListener("change",e=>{week=e.target.value;render();});
}

function render(){
  const rows=DATA[dim].map(r=>{const c=cell(r);return{name:r.name,players:c.players,games:c.games,wins:c.wins,wr:wr(c),row:r};})
    .filter(r=>r.players>0||r.games>0);
  const maxP=Math.max(1,...rows.map(r=>r.players));
  const totP=rows.reduce((a,r)=>a+r.players,0)||1;
  rows.sort((a,b)=>{
    let A,B;
    if(sortKey==="name"){A=a.name.toLowerCase();B=b.name.toLowerCase();return (A<B?-1:A>B?1:0)*sortDir;}
    if(sortKey==="wr"){A=a.wr==null?-1:a.wr;B=b.wr==null?-1:b.wr;}
    else{A=a[sortKey];B=b[sortKey];}
    return (A-B)*sortDir || b.players-a.players;
  });
  const wkLabel = week==="__ALL__"?"all weeks":week==="__T4__"?"last 4 weeks"
    :"week of "+((DATA.weeks.find(w=>w.start===week)||{}).label||week);
  document.getElementById("count").textContent=
    `${rows.length} ${dim==="faction"?"factions":dim+"s"} · ${wkLabel}`;
  document.getElementById("foot-n").textContent=`${totP.toLocaleString()} lists · ${rows.reduce((a,r)=>a+r.games,0).toLocaleString()} game-sides`;

  const cols=[["name","Name","l"],["players","Field share",""],["games","Games",""],["wr","Win rate",""]];
  document.querySelector("#tbl thead").innerHTML="<tr><th></th>"+cols.map(([k,label,cls])=>{
    const on=k===sortKey; return `<th class="${cls}" data-k="${k}" ${on?`aria-sort="${sortDir<0?"descending":"ascending"}"`:""}>${label}${on?`<span class="ar">${sortDir<0?"▼":"▲"}</span>`:""}</th>`;
  }).join("")+"</tr>";
  document.querySelector("#tbl tbody").innerHTML=rows.map((r,i)=>{
    const share=(100*r.players/totP);
    const barw=Math.round(96*r.players/maxP);
    const wtxt=r.wr==null?`<span class="dash">—</span>`:`${(100*r.wr).toFixed(0)}%`;
    const fillw=r.wr==null?0:Math.round(96*Math.min(1,Math.max(0,r.wr)));
    const low=r.wr!=null&&r.games<DATA.low_n?`<span class="flag" title="only ${r.games} games — noisy">⚠</span>`:"";
    return `<tr>
      <td class="rank num">${i+1}</td>
      <td class="name l">${esc(r.name)}</td>
      <td><div class="share"><small class="num">${share.toFixed(1)}%</small><span class="bar" style="width:${barw}px"></span><span class="num" style="width:34px;text-align:right">${r.players}</span></div></td>
      <td class="num">${r.games.toLocaleString()}</td>
      <td><div class="wr">${low}<div class="track"><div class="fill" style="width:${fillw}px;background:${pctColor(r.wr)}"></div></div><b class="num" style="color:${pctColor(r.wr)}">${wtxt}</b></div></td>
    </tr>`;
  }).join("");
  document.querySelectorAll("#tbl thead th[data-k]").forEach(th=>th.onclick=()=>{
    const k=th.dataset.k; if(k===sortKey)sortDir*=-1; else{sortKey=k;sortDir=(k==="name")?1:-1;} render();
  });
  drawChart(rows);
}

function drawChart(rows){
  const svg=document.getElementById("chart"), W=720,H=240,L=44,R=14,T=16,B=34;
  const weeks=DATA.weeks; const top=rows.slice(0,6).map(r=>r.row);
  const cap=document.getElementById("chartcap");
  if(weeks.length<1||!top.length){svg.innerHTML="";cap.textContent="No data.";document.getElementById("legend").innerHTML="";return;}
  cap.textContent=`Top ${top.length} ${dim==="faction"?"factions":dim+"s"} by field share · weekly win rate (games-weighted). 50% = even.`;
  const xs=weeks.map((w,i)=>weeks.length===1?(L+(W-L-R)/2):(L+i*(W-L-R)/(weeks.length-1)));
  const y0=0.35,y1=0.65, y=v=>T+(1-(Math.min(y1,Math.max(y0,v))-y0)/(y1-y0))*(H-T-B);
  let g="";
  // gridlines + y labels
  for(const gv of [0.40,0.45,0.50,0.55,0.60]){
    const yy=y(gv), fifty=gv===0.50;
    g+=`<line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" stroke="var(--grid)" stroke-width="${fifty?1.4:1}" ${fifty?'stroke-dasharray="4 3"':''}/>`;
    g+=`<text x="${L-8}" y="${yy+3.5}" text-anchor="end" font-size="10" fill="var(--faint)">${(gv*100).toFixed(0)}%</text>`;
  }
  weeks.forEach((w,i)=>{g+=`<text x="${xs[i]}" y="${H-12}" text-anchor="middle" font-size="10.5" fill="var(--muted)">${w.short||w.label}</text>`;});
  top.forEach((r,ti)=>{
    const col=LINE[ti%LINE.length];
    const pts=weeks.map((w,i)=>{const c=r.byweek[w.start];const v=(c&&c.games)?c.wins/c.games:null;return v==null?null:[xs[i],y(v),c.games];}).filter(Boolean);
    if(pts.length>1){g+=`<polyline fill="none" stroke="${col}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" points="${pts.map(p=>p[0]+","+p[1]).join(" ")}"/>`;}
    pts.forEach(p=>{g+=`<circle cx="${p[0]}" cy="${p[1]}" r="${pts.length===1?4:3.2}" fill="${col}"><title>${esc(r.name)} · ${(100*(p[1]?0:0))}</title></circle>`;});
  });
  svg.innerHTML=g;
  document.getElementById("legend").innerHTML=top.map((r,ti)=>`<span><i style="background:${LINE[ti%LINE.length]}"></i>${esc(r.name)}</span>`).join("");
}

initChrome(); render();
</script>
</body>
</html>
"""


def render(data):
    return _TMPL.replace("__DATA__", json.dumps(data, separators=(",", ":")))
