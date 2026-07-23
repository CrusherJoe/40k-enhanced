"""Generate YAML for the 4 IK base-Codex detachments from the 39k.pro bundle."""
import re, html, yaml
import extract as e

# detachmentId -> (key, name, disposition, dp)  [disposition/dp already known/authoritative]
BASE = {
    "xx05BPfG5pc": ("hallowed-martyrs",     "Hallowed Martyrs",     "priority-assets", 3),
    "e5-v9x7e_3I": ("bringers-of-flame",    "Bringers of Flame",    "purge-the-foe",   3),
    "taQhlvoMbA4": ("champions-of-faith",   "Champions of Faith",   "disruption",      2),
    "kd0TKv_266Q": ("army-of-faith",        "Army of Faith",        "take-and-hold",   2),
    "UadV8wR-9Ts": ("penitent-host",        "Penitent Host",        "take-and-hold",   2),
    "gYMh8spPhjM": ("chorus-of-condemnation","Chorus of Condemnation","reconnaissance", 1),
    "RlhRPTTgvRQ": ("sanctified-orators",   "Sanctified Orators",   "purge-the-foe",   1),
    "OZozSigbmSM": ("sacred-champions",     "Sacred Champions",     "take-and-hold",   1),
}

PHASE = {"yourTurn": "Your turn", "opponentsTurn": "Opponent's turn",
         "anyTurn": "Any turn", "eitherPlayersTurn": "Either player's turn"}
CAT = {"battleTactic": "Battle Tactic", "epicDeed": "Epic Deed",
       "strategicPloy": "Strategic Ploy", "wargear": "Wargear"}


def unescape(s):
    if s is None:
        return None
    s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
    for a, b in [('\\"', '"'), ("\\'", "'"), ('\\/', '/'), ('\\n', '\n'),
                 ('\\t', '\t'), ('\\\\', '\\')]:
        s = s.replace(a, b)
    s = html.unescape(s)          # &#x20; &nbsp; etc.
    s = s.replace('‑', '-')  # non-breaking hyphen -> plain hyphen
    return s.strip()


def order(recs):
    return sorted(recs, key=lambda r: int(e.field(r, 'displayOrder') or 0))


# Pre-load tables once
T = {t: e.table(t) for t in ['detachment_rule', 'rule_container_component',
                             'enhancement', 'stratagem']}
RCC = list(e.records(T['rule_container_component']))


def rule_for(det_id):
    rec = next((r for r in e.records(T['detachment_rule'])
                if f'detachmentId:"{det_id}"' in r), None)
    if not rec:
        return None
    rid = e.field(rec, 'id')
    name = unescape(e.en_field(rec, 'name'))
    comps = [r for r in RCC if f'detachmentRuleId:"{rid}"' in r]
    body, lore = [], []
    for c in order(comps):
        txt = unescape(e.en_field(c, 'textContent'))
        if not txt:
            continue
        (lore if e.field(c, 'type') == 'loreAccordion' else body).append(txt)
    out = {"name": name, "text": "\n\n".join(body)}
    if lore:
        out["lore"] = "\n\n".join(lore)
    return out


def enhancements_for(det_id):
    recs = [r for r in e.records(T['enhancement']) if f'detachmentId:"{det_id}"' in r]
    out = []
    for r in order(recs):
        pts = e.field(r, 'basePointsCost')
        out.append({
            "name": unescape(e.en_field(r, 'name')),
            "points": int(pts) if pts and pts.isdigit() else None,
            "text": unescape(e.en_field(r, 'rules')),
        })
    return out


def stratagems_for(det_id):
    recs = [r for r in e.records(T['stratagem']) if f'detachmentId:"{det_id}"' in r]
    out = []
    for r in order(recs):
        cp = e.field(r, 'cpCost')
        item = {
            "name": unescape(e.en_field(r, 'name')),
            "cp": int(cp) if cp and cp.isdigit() else cp,
            "type": CAT.get(e.field(r, 'category'), e.field(r, 'category')),
            "when": unescape(e.en_field(r, 'whenRules')),
            "target": unescape(e.en_field(r, 'targetRules')),
            "effect": unescape(e.en_field(r, 'effectRules')),
        }
        restr = unescape(e.en_field(r, 'restrictionRules'))
        if restr:
            item["restriction"] = restr
        out.append(item)
    return out


detachments = []
for det_id, (key, name, disp, dp) in BASE.items():
    detachments.append({
        "key": key, "name": name, "source": "codex",
        "disposition": disp, "dp": dp,
        "rule": rule_for(det_id),
        "enhancements": enhancements_for(det_id),
        "stratagems": stratagems_for(det_id),
    })

# quick sanity print
for d in detachments:
    print(f"{d['name']:<22} rule={d['rule']['name']!r:<22} "
          f"enh={len(d['enhancements'])} strat={len(d['stratagems'])}")

with open('sisters_detachments_rules.yaml', 'w', encoding='utf-8') as fh:
    yaml.dump(detachments, fh, allow_unicode=True, sort_keys=False, width=100,
              default_flow_style=False)
print("\nwrote sisters_detachments_rules.yaml")
