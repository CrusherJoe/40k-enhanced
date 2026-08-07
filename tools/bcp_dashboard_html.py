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
.lead{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 16px;margin:0 0 18px;padding:12px 16px;
  background:var(--surface);border:1px solid var(--border);border-radius:12px}
.lead .eyebrow{align-self:center}
.lchip{display:inline-flex;align-items:baseline;gap:6px;font-size:15px}
.lchip .medal{font-size:15px}
.lchip small{color:var(--muted);font-size:12px}
.chartcard{padding:18px 18px 10px;margin-bottom:18px}
.chartcard h2,.tablecard h2{font-size:13px;margin:0 0 2px;font-weight:650}
.chartcard .cap{font-size:12px;color:var(--muted);margin:0 0 8px}
.chartwrap{overflow-x:auto}
svg{display:block;width:100%;height:auto;min-width:560px}
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
.share .tbar{background:var(--good);opacity:.5}
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

  <div class="lead" id="leaders"></div>

  <div class="card chartcard">
    <h2>Win rate &amp; use % over time</h2>
    <p class="cap" id="chartcap"></p>
    <div class="chartwrap"><svg id="chart" viewBox="0 0 720 340" preserveAspectRatio="xMidYMid meet"></svg></div>
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
const LINE = ["#e0a53a","#4c9be8","#43c08e","#c77dd6","#e56b62","#6fc7c0",
              "#f0883c","#7d8ff0","#db5fa0","#a7c23e"];
let dim="faction", week="__ALL__", sortKey="players", sortDir=-1;

const wr = r => r.games ? r.wins/r.games : null;
const pctColor = p => p==null ? "var(--mid)" : p>=0.52 ? "var(--good)" : p<=0.48 ? "var(--bad)" : "var(--mid)";
const esc = s => (s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

const T4=()=>DATA.weeks.slice(-4).map(w=>w.start);   // last up-to-4 meta weeks
function cell(row){                     // resolve a row's stats for the current week filter
  if(week==="__ALL__") return {...row.total};
  const keys = week==="__T4__" ? T4() : [week];
  const o={games:0,wins:0,players:0,top:0};
  for(const k of keys){const w=row.byweek[k]; if(w){o.games+=w.games;o.wins+=w.wins;o.players+=w.players;o.top+=(w.top||0);}}
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
    `from army-list text, so it is only as complete as the list corpus — win rates on fewer than ${DATA.low_n} games are flagged as noisy. `+
    `<b>Top ${DATA.top_cut_n||8} share</b> = share among each event's top-${DATA.top_cut_n||8} finishers (the competitive cut); `+
    `<b>Δ</b> = top-cut minus field share — <b>positive = over-represented among winners</b>, negative = a "trap".`;
  document.getElementById("gen").textContent=DATA.generated_utc.replace("T"," ").replace("Z"," UTC");
  const sel=document.getElementById("weeksel");
  const t4=DATA.weeks.length>1?`<option value="__T4__">Last 4 weeks</option>`:"";
  sel.innerHTML=`<option value="__ALL__">All weeks (cumulative)</option>`+t4+
    DATA.weeks.map(w=>`<option value="${w.start}">Week of ${w.label}${w.in_progress?" (in progress)":""}</option>`).join("");
  document.getElementById("dimseg").addEventListener("click",e=>{
    const b=e.target.closest("button"); if(!b)return;
    dim=b.dataset.dim; [...e.currentTarget.children].forEach(x=>x.setAttribute("aria-pressed",x===b));
    sortKey="players";sortDir=-1; render();
  });
  sel.addEventListener("change",e=>{week=e.target.value;render();});
}

const dColor=d=>d>=0.01?"var(--good)":d<=-0.01?"var(--bad)":"var(--mid)";
function render(){
  const rows=DATA[dim].map(r=>{const c=cell(r);return{name:r.name,players:c.players,top:c.top||0,games:c.games,wins:c.wins,wr:wr(c),row:r};})
    .filter(r=>r.players>0||r.games>0);
  const maxP=Math.max(1,...rows.map(r=>r.players));
  const totP=rows.reduce((a,r)=>a+r.players,0)||1;
  const totT=rows.reduce((a,r)=>a+r.top,0);            // total top-8 slots in view (0 if no results yet)
  const hasTop=totT>0;
  rows.forEach(r=>{r.share=r.players/totP; r.topshare=hasTop?r.top/totT:0; r.delta=r.topshare-r.share;});
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
  document.getElementById("foot-n").textContent=
    `${totP.toLocaleString()} lists · ${totT.toLocaleString()} top-${DATA.top_cut_n||8} · ${rows.reduce((a,r)=>a+r.games,0).toLocaleString()} game-sides`;

  // "top win rate" leaders strip (min-n guarded so a 3-game fluke can't top it)
  const dname={faction:"faction",disposition:"disposition",detachment:"detachment"}[dim];
  const elig=rows.filter(r=>r.wr!=null&&r.games>=DATA.low_n).sort((a,b)=>b.wr-a.wr).slice(0,3);
  const medals=["🥇","🥈","🥉"];
  document.getElementById("leaders").innerHTML=
    `<span class="eyebrow">Top win rate · ${dname} · ${wkLabel}</span>`+
    (elig.length?elig.map((r,i)=>`<span class="lchip"><span class="medal">${medals[i]}</span> <b>${esc(r.name)}</b> `
      +`<b class="num" style="color:${pctColor(r.wr)}">${(100*r.wr).toFixed(0)}%</b> <small class="num">${r.games} games</small></span>`).join("")
     :`<span class="lchip"><span class="dash">not enough games yet (need ≥${DATA.low_n})</span></span>`);

  const N=DATA.top_cut_n||8;
  const cols=[["name","Name","l"],["players","Field share",""],["top",`Top ${N} share`,""],
              ["delta","Δ top−field",""],["wr","Win rate",""]];
  document.querySelector("#tbl thead").innerHTML="<tr><th></th>"+cols.map(([k,label,cls])=>{
    const on=k===sortKey; return `<th class="${cls}" data-k="${k}" title="${k==='delta'?'top-'+N+' share minus field share — positive = over-represented among winners':''}">${label}${on?`<span class="ar">${sortDir<0?"▼":"▲"}</span>`:""}</th>`;
  }).join("")+"</tr>";
  const maxT=Math.max(1,...rows.map(r=>r.top));
  document.querySelector("#tbl tbody").innerHTML=rows.map((r,i)=>{
    const barw=Math.round(84*r.players/maxP), tbarw=Math.round(84*r.top/maxT);
    const wtxt=r.wr==null?`<span class="dash">—</span>`:`${(100*r.wr).toFixed(0)}%`;
    const fillw=r.wr==null?0:Math.round(96*Math.min(1,Math.max(0,r.wr)));
    const low=r.wr!=null&&r.games<DATA.low_n?`<span class="flag" title="only ${r.games} games — noisy">⚠</span>`:"";
    const topCell=hasTop
      ? `<div class="share"><small class="num">${(100*r.topshare).toFixed(1)}%</small><span class="bar tbar" style="width:${tbarw}px"></span><span class="num" style="width:28px;text-align:right">${r.top}</span></div>`
      : `<span class="dash">—</span>`;
    const dtxt=hasTop?`<b class="num" style="color:${dColor(r.delta)}">${r.delta>=0?"+":"−"}${(Math.abs(100*r.delta)).toFixed(1)}</b>`:`<span class="dash">—</span>`;
    return `<tr>
      <td class="rank num">${i+1}</td>
      <td class="name l">${esc(r.name)}</td>
      <td><div class="share" title="${r.players} of ${totP} lists"><small class="num">${(100*r.share).toFixed(1)}%</small><span class="bar" style="width:${barw}px"></span><span class="num" style="width:28px;text-align:right">${r.players}</span></div></td>
      <td>${topCell}</td>
      <td class="num">${dtxt}</td>
      <td><div class="wr">${low}<div class="track"><div class="fill" style="width:${fillw}px;background:${pctColor(r.wr)}"></div></div><b class="num" style="color:${pctColor(r.wr)}">${wtxt}</b></div></td>
    </tr>`;
  }).join("");
  document.querySelectorAll("#tbl thead th[data-k]").forEach(th=>th.onclick=()=>{
    const k=th.dataset.k; if(k===sortKey)sortDir*=-1; else{sortKey=k;sortDir=(k==="name")?1:-1;} render();
  });
  drawChart(rows);
}

function drawChart(rows){
  const svg=document.getElementById("chart"), W=720,H=340,L=46,R=48,T=18,B=40;
  const weeks=DATA.weeks; const top=rows.slice(0,10).map(r=>r.row);
  const cap=document.getElementById("chartcap");
  if(weeks.length<1||!top.length){svg.innerHTML="";cap.textContent="No data.";document.getElementById("legend").innerHTML="";return;}
  const anyIP=weeks.some(w=>w.in_progress);
  const wkTot={}; weeks.forEach(w=>{wkTot[w.start]=DATA[dim].reduce((a,r)=>a+((r.byweek[w.start]||{}).players||0),0);});
  const wr =c=>(c&&c.games)?c.wins/c.games:null;
  const use=(c,ws)=>(c&&wkTot[ws])?c.players/wkTot[ws]:null;
  cap.innerHTML=`Top ${top.length} ${dim==="faction"?"factions":dim+"s"} by field share · <b>solid = win rate</b> (left axis) · `
    +`<b>dotted = use %</b> (right axis).`+(anyIP?" Win rate is shown for completed weeks only; use % includes the current week's registered field.":"");
  const xs=weeks.map((w,i)=>weeks.length===1?(L+(W-L-R)/2):(L+i*(W-L-R)/(weeks.length-1)));
  const yW=v=>T+(1-(Math.min(.65,Math.max(.35,v))-.35)/.30)*(H-T-B);   // LEFT: win rate 35-65%
  // RIGHT: use % 0..nice-max
  let mx=0; top.forEach(r=>weeks.forEach(w=>{const v=use(r.byweek[w.start],w.start); if(v!=null)mx=Math.max(mx,v);}));
  const raw=Math.max(mx,0.04)/4, mag=Math.pow(10,Math.floor(Math.log10(raw)));
  const ustep=[1,2,2.5,5,10].map(m=>m*mag).find(s=>s>=raw)||10*mag, u1=Math.ceil(mx/ustep)*ustep||ustep;
  const yU=v=>T+(1-(Math.min(u1,Math.max(0,v)))/u1)*(H-T-B);
  let g="";
  for(const gv of [0.40,0.45,0.50,0.55,0.60]){const yy=yW(gv),fifty=gv===0.50;
    g+=`<line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" stroke="var(--grid)" stroke-width="${fifty?1.4:1}" ${fifty?'stroke-dasharray="4 3"':''}/>`;
    g+=`<text x="${L-9}" y="${yy+4}" text-anchor="end" font-size="12" fill="var(--faint)">${(gv*100).toFixed(0)}%</text>`;}
  for(let t=0;t<=u1+1e-9;t+=ustep){g+=`<text x="${W-R+8}" y="${yU(t)+4}" text-anchor="start" font-size="12" fill="var(--faint)">${(t*100).toFixed(t>0&&t<0.1?1:0)}%</text>`;}
  weeks.forEach((w,i)=>{g+=`<text x="${xs[i]}" y="${H-14}" text-anchor="middle" font-size="13" fill="var(--muted)">${w.short||w.label}</text>`;});
  top.forEach((r,ti)=>{
    const col=LINE[ti%LINE.length];
    // use % (dotted, right axis, secondary) — drawn first so win-rate lines sit on top
    const up=weeks.map((w,i)=>{const v=use(r.byweek[w.start],w.start);return v==null?null:[xs[i],yU(v)];});
    for(let i=0;i<up.length-1;i++){const a=up[i],b=up[i+1];if(!a||!b)continue;
      g+=`<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${col}" stroke-width="1.5" stroke-dasharray="1.5 3.5" opacity="0.5"/>`;}
    up.forEach(p=>{if(p)g+=`<circle cx="${p[0]}" cy="${p[1]}" r="2" fill="${col}" opacity="0.5"/>`;});
    // win rate (solid, left axis, primary) — COMPLETED weeks only (an in-progress week's ~few games isn't a
    // win rate; plotting it clamps to the axis and dominates the chart with noise)
    const wp=weeks.map((w,i)=>{if(w.in_progress)return null;const v=wr(r.byweek[w.start]);
      return v==null?null:{x:xs[i],y:yW(v),g:(r.byweek[w.start]||{}).games,v};});
    for(let i=0;i<wp.length-1;i++){const a=wp[i],b=wp[i+1];if(!a||!b)continue;
      g+=`<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="${col}" stroke-width="2.6" stroke-linecap="round"/>`;}
    wp.forEach(p=>{if(!p)return;
      g+=`<circle cx="${p.x}" cy="${p.y}" r="3.6" fill="${col}"><title>${esc(r.name)} · win ${(100*p.v).toFixed(0)}% (${p.g} games)</title></circle>`;});
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
