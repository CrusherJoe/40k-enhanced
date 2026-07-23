"""Regenerate all Imperial Knights datasheet profiles from the BSData wh40k-11e
catalogue (ik_lib.json). Authoritative replacement for the hand-transcribed file.

BattleScribe/BSData model:
- datasheet = a `model`/`unit` sharedSelectionEntry
- stat line  = its "Unit" typeName profile (M/T/Sv/W/LD/OC/InSv)
- weapons    = "Ranged/Melee Weapons" profiles reachable through its wargear tree
               (selectionEntries + selectionEntryGroups + entryLinks -> shared)
- abilities  = "Abilities" profiles + infoGroups (Bondsman) + rule infoLinks
               (Deadly Demise / Code Chivalric / Super-Heavy Walker); the Deadly
               Demise value is an `append` modifier on the infoLink name.
- damaged    = a "Damaged: ..." profile infoLink (name = threshold, desc = text)
- keywords   = categoryLinks
- points     = costs.pts  (cross-checked against MFM; MFM stays source of truth)
"""
import json
import re
import yaml

cat = json.load(open('sisters.json'))['catalogue']
SSE = {e['id']: e for e in cat['sharedSelectionEntries']}
SSEG = {g['id']: g for g in cat.get('sharedSelectionEntryGroups', [])}
SP = {p['id']: p for p in cat.get('sharedProfiles', [])}
SR = {r['id']: r for r in cat.get('sharedRules', [])}

# Unit-level ability rules to keep. Other rule infoLinks (Sustained Hits, Blast,
# Devastating Wounds, ...) are WEAPON keywords that link in via weapons -- skip
# them here since they're already captured on the weapon profiles.
CORE_RULES = {'Deadly Demise', 'Lone Operative', 'Feel No Pain', 'Scouts', 'Infiltrators', 'Deep Strike', 'Fights First', 'Stealth'}
FACTION_RULES = {'Shield of Faith', 'Acts of Faith', 'Sacred Rites', 'Martyrdom'}


def ch(p):
    return {c['name']: c.get('$text') for c in p.get('characteristics', [])}


def clean_text(s):
    if not s:
        return s
    s = s.replace('^^', '').replace('**', '')
    return re.sub(r'\s+', ' ', s).strip()


def clean_name(s):
    return re.sub(r'^[^0-9A-Za-z]+', '', s or '').strip()


def num(v):
    """int for plain integers (incl. negative), else the string as-is."""
    if v is None:
        return None
    if re.fullmatch(r'-?\d+', v.strip()):
        return int(v)
    return v.strip()


def kw_list(s):
    if not s or s == '-':
        return []
    return [k.strip().upper() for k in s.split(',') if k.strip()]


def resolve_rule_name(il):
    """Apply infoLink name modifiers (e.g. append 'D6') to a rule link name."""
    name = il.get('name', '')
    for m in il.get('modifiers', []):
        if m.get('field') == 'name':
            if m.get('type') == 'append':
                name = f"{name} {m['value']}".strip()
            elif m.get('type') == 'set':
                name = m['value']
    return name


def collect_weapons(entry, seen, out):
    for p in entry.get('profiles', []):
        tn = p.get('typeName', '')
        if tn in ('Ranged Weapons', 'Melee Weapons'):
            nm = clean_name(p['name'])
            if nm not in seen:
                seen.add(nm)
                out.append((tn, nm, ch(p)))
    for se in entry.get('selectionEntries', []):
        collect_weapons(se, seen, out)
    for g in entry.get('selectionEntryGroups', []):
        collect_weapons(g, seen, out)
    for el in entry.get('entryLinks', []):
        tgt = SSE.get(el.get('targetId')) or SSEG.get(el.get('targetId'))
        if tgt:
            collect_weapons(tgt, seen, out)


def weapon_dict(tn, name, c):
    d = {'name': name}
    if tn == 'Ranged Weapons':
        rng = c.get('Range', '')
        d['range'] = num(rng.replace('"', '')) if rng and rng != '-' else rng
        d['A'] = num(c.get('A'))
        d['BS'] = c.get('BS')
    else:
        d['A'] = num(c.get('A'))
        d['WS'] = c.get('WS')
    d['S'] = num(c.get('S'))
    d['AP'] = num(c.get('AP'))
    d['D'] = num(c.get('D'))
    kw = kw_list(c.get('Keywords'))
    if kw:
        d['abilities'] = kw
    return d


def option_lines(entry):
    """Best-effort readable wargear-swap lines from the entry's groups."""
    out = []
    for g in entry.get('selectionEntryGroups', []):
        opts = [se.get('name') for se in g.get('selectionEntries', [])]
        opts += [clean_name(el.get('name') or SSE.get(el.get('targetId'), {}).get('name', ''))
                 for el in g.get('entryLinks', [])]
        opts = [o for o in opts if o]
        if opts:
            out.append(f"{g.get('name', 'Wargear')}: " + " / ".join(opts))
    return out


def profile_source(entry):
    """Return (src_entry_with_Unit_profile, [extra_model_entries]).

    Most datasheets carry the Unit profile directly. A `unit` wrapper (Canis Rex)
    holds it on nested `model` sub-entries instead (the knight + its pilot).
    """
    if any(p.get('typeName') == 'Unit' for p in entry.get('profiles', [])):
        return entry, []
    models = [s for s in entry.get('selectionEntries', [])
              if s.get('type') == 'model' and any(p.get('typeName') == 'Unit' for p in s.get('profiles', []))]
    if not models:
        return None, []
    primary = next((m for m in models if m['name'] == entry['name']), models[0])
    return primary, [m for m in models if m is not primary]


def build(entry):
    src, extra_models = profile_source(entry)
    if src is None:
        return None
    unit_profiles = [p for p in src.get('profiles', []) if p.get('typeName') == 'Unit']
    display_name = entry['name']
    st = ch(unit_profiles[0])
    insv = st.get('InSv', '') or ''
    prof = {
        'name': display_name,
        'source': 'bsdata-wh40k-11e',
        'stats': {
            'M': num((st.get('M') or '').replace('"', '')),
            'T': num(st.get('T')),
            'Sv': st.get('Sv'),
            'W': num(st.get('W')),
            'Ld': st.get('LD'),
            'OC': num(st.get('OC')),
        },
    }
    if insv and insv not in ('-', ''):
        prof['invuln'] = insv.replace('*', '')
        prof['invuln_ranged_only'] = insv.endswith('*')

    weps = []
    collect_weapons(src, set(), weps)
    ranged = [weapon_dict(tn, nm, c) for tn, nm, c in weps if tn == 'Ranged Weapons']
    melee = [weapon_dict(tn, nm, c) for tn, nm, c in weps if tn == 'Melee Weapons']
    if ranged:
        prof['ranged'] = ranged
    if melee:
        prof['melee'] = melee

    core, faction, datasheet = [], [], []
    for il in src.get('infoLinks', []):
        if il.get('type') == 'rule':
            base = il.get('name', '')
            if base in CORE_RULES:
                core.append(resolve_rule_name(il))
            elif base in FACTION_RULES:
                faction.append(resolve_rule_name(il))
            # else: weapon-keyword rule -> skip (captured on weapons)
    for p in src.get('profiles', []):
        if p.get('typeName') == 'Abilities':
            datasheet.append({'name': p['name'], 'text': clean_text(ch(p).get('Description'))})
    for ig in src.get('infoGroups', []):
        for p in ig.get('profiles', []):
            datasheet.append({'name': ig.get('name'), 'text': clean_text(ch(p).get('Description'))})
    ab = {}
    if core:
        ab['core'] = core
    if faction:
        ab['faction'] = faction
    if datasheet:
        ab['datasheet'] = datasheet
    if ab:
        prof['abilities'] = ab

    # damaged bracket (profile infoLink)
    for il in src.get('infoLinks', []):
        if il.get('type') == 'profile' and (il.get('name') or '').startswith('Damaged'):
            tgt = SP.get(il.get('targetId'))
            thr = re.search(r'([\d]+-[\d]+)', il.get('name', ''))
            prof['damaged'] = {
                'threshold': thr.group(1) if thr else il.get('name'),
                'text': clean_text((ch(tgt).get('Description') if tgt else '') or ''),
            }
            break

    prof['keywords'] = [cl['name'] for cl in src.get('categoryLinks', [])
                        if not cl['name'].startswith('Faction:')]
    # (wargear swaps are omitted: the ranged/melee lists already enumerate the
    # datasheet's full weapon arsenal, and BSData's group structure doesn't
    # cleanly separate optional swaps from fixed gear.)

    # secondary stat lines (e.g. Canis Rex's pilot Sir Hekhtur)
    if extra_models:
        prof['extra_profiles'] = []
        for m in extra_models:
            s = ch(next(p for p in m['profiles'] if p.get('typeName') == 'Unit'))
            prof['extra_profiles'].append({
                'name': m['name'],
                'stats': {'M': num((s.get('M') or '').replace('"', '')), 'T': num(s.get('T')),
                          'Sv': s.get('Sv'), 'W': num(s.get('W')), 'Ld': s.get('LD'), 'OC': num(s.get('OC'))},
            })
    return prof


datasheets = []
for e in cat['sharedSelectionEntries']:
    if e['type'] in ('model', 'unit'):
        p = build(e)
        if p:
            datasheets.append(p)
datasheets.sort(key=lambda d: d['name'])

# --- points cross-check vs MFM ---
mfm = {d['name']: d['points_first']
       for d in yaml.safe_load(open('sisters_datasheets.yaml'))}
print(f"built {len(datasheets)} profiles\n")
print("points cross-check (BSData costs.pts vs MFM points_first):")
for e in cat['sharedSelectionEntries']:
    if e['type'] in ('model', 'unit'):
        bs = next((c['value'] for c in e.get('costs', []) if c['name'] == 'pts'), None)
        m = mfm.get(e['name'])
        flag = '' if bs == m else '   <-- MISMATCH'
        if flag or bs != m:
            print(f"  {e['name']:<28} BSData={bs}  MFM={m}{flag}")

with open('sisters_profiles.yaml', 'w', encoding='utf-8') as fh:
    yaml.dump(datasheets, fh, allow_unicode=True, sort_keys=False, width=100, default_flow_style=False)
print("\nwrote sisters_profiles.yaml")
