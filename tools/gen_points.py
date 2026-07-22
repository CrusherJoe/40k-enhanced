"""Extract IK datasheet points from the MFM SSR page (mfm.html).

Structure: React streaming SSR. Each datasheet is a sequence of <div hidden
id="S:N"> suspense payloads in hex order:
  - a NAME slot (uppercase unit name),
  - one or two UNIT-COST slots ("395 pts" = 1st unit; a 2nd = each 2nd+ unit),
  - optionally WARGEAR-OPTION cost slots, whose S-index is identified by a
    'WARGEAR OPTIONS ... per <name> ... <template id="P:N">' block.
A trailing "▲ (+N)" marks a recent points *increase*, not a cost to add.
"""
import re, html, yaml

h = open('mfm.html', encoding='utf-8').read()


def clean(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s))).strip()


# 1) suspense payload slots in hex order
divs = re.findall(r'<div hidden id="S:([0-9a-f]+)">(.*?)</div>\s*<script>\$RS', h, re.S)
slot = {int(sid, 16): clean(c) for sid, c in divs}

# 2) wargear-option slots: S-index -> wargear name. Markup:
#    <li><span>per <NAME></span><template id="P:N"></template></li>
wargear = {}
for m in re.finditer(r'<span>per ([^<]+)</span><template id="P:([0-9a-f]+)"', h):
    wargear[int(m.group(2), 16)] = m.group(1).strip()

PTS = re.compile(r'^(?:▲\s*)?(?:\(\+\d+\)\s*)?(\d+)\s*pts$')
NAME = re.compile(r'^[A-Z0-9 \'’.\-▲]+$')

units = []
for idx in sorted(slot):
    txt = slot[idx]
    m = PTS.match(txt)
    if m:
        pts = int(m.group(1))
        if not units:
            continue
        if idx in wargear:
            units[-1]['wargear'].append({'name': wargear[idx], 'points': pts})
        else:
            units[-1]['costs'].append(pts)
    elif txt and NAME.match(txt) and 'COST' not in txt and 'UNIT' not in txt \
            and 'WARGEAR' not in txt and 'OPTION' not in txt and len(txt) < 40 \
            and any(c.isalpha() for c in txt):
        units.append({'name': txt.replace('▲', '').strip().title(), 'costs': [], 'wargear': []})

datasheets = []
for u in units:
    if not u['costs']:
        continue
    d = {'name': u['name'], 'points_first': u['costs'][0]}
    if len(u['costs']) > 1:
        d['points_additional'] = u['costs'][1]
    if u['wargear']:
        d['wargear'] = u['wargear']
    datasheets.append(d)

print(f"datasheets: {len(datasheets)}  wargear-slots: {wargear}\n")
for d in datasheets:
    add = f" / +{d['points_additional']} each" if 'points_additional' in d else ""
    wg = "  wargear=" + str(d['wargear']) if 'wargear' in d else ""
    print(f"  {d['name']:<28} {d['points_first']}{add}{wg}")

with open('datasheets.yaml', 'w', encoding='utf-8') as fh:
    yaml.dump(datasheets, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)
