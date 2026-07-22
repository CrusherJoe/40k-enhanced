"""String-aware extractor for the 39k.pro Vite bundle's embedded relational data.

Records are minified JS object literals. Rules text contains [BRACKETS], {braces}
and both ' and " quotes, so bracket-matching MUST respect string literals.
"""
import re, sys, json

JS = open('app.js', encoding='utf-8', errors='replace').read()


def match_bracket(s, i):
    """Given s[i] is an opening [ or {, return index of its matching close,
    skipping over JS string literals ('...' and \"...\" with backslash escapes)."""
    open_c = s[i]; close_c = {'[': ']', '{': '}'}[open_c]
    depth = 0; quote = None; j = i
    while j < len(s):
        c = s[j]
        if quote:
            if c == '\\':
                j += 2; continue
            if c == quote:
                quote = None
        else:
            if c in ("'", '"', '`'):
                quote = c
            elif c == open_c:
                depth += 1
            elif c == close_c:
                depth -= 1
                if depth == 0:
                    return j
        j += 1
    raise ValueError("unbalanced")


def table(name):
    """Return the array string for `name:[ ... ]` (top-level relation)."""
    m = re.search(r'(?<![A-Za-z_])' + re.escape(name) + r':\[', JS)
    if not m:
        return None
    i = m.end() - 1
    return JS[i:match_bracket(JS, i) + 1]


def records(arr):
    """Yield each top-level {...} record string inside array string `arr`."""
    j = 0
    while j < len(arr):
        if arr[j] == '{':
            end = match_bracket(arr, j)
            yield arr[j:end + 1]
            j = end + 1
        else:
            j += 1


def field(rec, key):
    """Extract a top-level scalar field key:value (string/number/bool/null)."""
    m = re.search(r'(?<![A-Za-z_])' + re.escape(key) + r':', rec)
    if not m:
        return None
    i = m.end()
    if rec[i] in ('"', "'", '`'):
        end = _str_end(rec, i)
        return rec[i + 1:end]
    m2 = re.match(r'(!?\d[\d.]*|!0|!1|null|true|false)', rec[i:])
    if not m2:
        return None
    tok = m2.group(0)
    return None if tok == 'null' else tok


def _str_end(s, i):
    q = s[i]; j = i + 1
    while j < len(s):
        if s[j] == '\\':
            j += 2; continue
        if s[j] == q:
            return j
        j += 1
    raise ValueError


def en_block(rec):
    """Return the {...} of the en: localisation, or None."""
    m = re.search(r'en:\{', rec)
    if not m:
        return None
    i = m.end() - 1
    return rec[i:match_bracket(rec, i) + 1]


def en_field(rec, key):
    b = en_block(rec)
    return field(b, key) if b else None


if __name__ == '__main__':
    # probe: which tables carry text for a detachment rule, using Valourstrike
    TARGET = 'FGVx0OgDRDY'
    for tbl in ['detachment_rule', 'detachment_detail', 'detachment_detail_bullet_point',
                'rule_container', 'rule_section', 'rule_container_component']:
        arr = table(tbl)
        if arr is None:
            print(f'{tbl}: NOT FOUND'); continue
        recs = [r for r in records(arr) if f'"{TARGET}"' in r]
        print(f'\n### {tbl}: {len(recs)} record(s) referencing {TARGET}')
        for r in recs[:3]:
            print('  head:', r[:120])
            b = en_block(r)
            if b:
                print('  en  :', b[:400])
