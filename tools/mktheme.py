#!/usr/bin/env python3
"""mktheme.py <scheme.json> <pairs.tsv> <out.json> [Anzeigename]
Baut ein VS-Code-Theme aus Vim-Farbdump (vimdump.vim) + gelernter Scope->Gruppe-Zuordnung."""
import csv, collections, json, sys, re

dump, pairs, out = sys.argv[1:4]
D = json.load(open(dump))
G = D['groups']
dark = D['background'] == 'dark'
name = sys.argv[4] if len(sys.argv) > 4 else 'Vim: ' + D['scheme']

def hx(c): return c.lstrip('#')
def rgb(c): c = hx(c); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
def tohex(t): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in t)
def blend(a, b, t): return tohex(tuple(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))
def alpha(c, a): return c + '%02x' % round(a * 255)

N = G.get('Normal', {})
NFG = N.get('fg') or ('#ffffff' if dark else '#000000')
NBG = N.get('bg') or ('#000000' if dark else '#ffffff')

def eff(g, fb_fg=None, fb_bg=None):
    """(fg, bg, bold, italic, underline) einer Gruppe, reverse aufgelöst."""
    x = G.get(g)
    if not x: return (fb_fg, fb_bg, 0, 0, 0)
    fg, bg = x['fg'] or None, x['bg'] or None
    if x['reverse']:
        fg, bg = (bg or NBG), (fg or NFG)
    return (fg or fb_fg, bg or fb_bg, x['bold'], x['italic'], x['underline'] or x['undercurl'])

import os as _os
LD = {}
if _os.environ.get('LANGDUMP'):
    LD = json.load(open(_os.environ['LANGDUMP']))
    for k, v in LD.items():
        G['lang:' + k] = v
        if k not in G and v.get('trans') == k: G[k] = v        # Gruppen ohne Link auf Standardgruppen
# ---- Token-Zuordnung: innerster Scope (mit Präfix-Rückfall) -> Standardgruppe
STD0 = [k for k in G if k in set('Comment Constant String Character Number Boolean Float Identifier Function Statement Conditional Repeat Label Operator Keyword Exception PreProc Include Define Macro PreCondit Type StorageClass Structure Typedef Special SpecialChar Tag Delimiter SpecialComment Debug Underlined Ignore Error Todo'.split())]
STD = STD0
EXTRA_OK = set(G) - set(STD0) - {'Normal'}
def embedded_in_markdown(r):
    # Codeblöcke in Markdown färbt Vim pauschal als markdownCodeBlock, nicht nach Sprache.
    # Diese Zeilen sagen nichts über die Farbe der eingebetteten Sprache (js, jsdoc, json, ...).
    return r['lang'].startswith('markdown/') and any(x.startswith('meta.embedded.') for x in r['tm_scopes'].split(' '))
m = collections.defaultdict(collections.Counter)       # ohne Codeblock-Zeilen aus Markdown
m_all = collections.defaultdict(collections.Counter)   # mit allen Zeilen: nur für die Eltern-Präfixe (Rückfall unbekannter Scopes)
for r in csv.DictReader(open(pairs), delimiter='\t', quoting=csv.QUOTE_NONE):
    inner = r['tm_scopes'].split(' ')[-1]
    g0 = r['vim_trans'] or 'None'
    k0 = g0 if (g0 in STD or g0 in EXTRA_OK) else 'None'
    m_all[inner][k0] += int(r['chars'])
    if not embedded_in_markdown(r): m[inner][k0] += int(r['chars'])
# Eltern-qualifizierte Zählung: (Elternscope, innerster Scope) -> Gruppe
mq = collections.defaultdict(collections.Counter)
for r in csv.DictReader(open(pairs), delimiter='\t', quoting=csv.QUOTE_NONE):
    if embedded_in_markdown(r): continue
    sc = r['tm_scopes'].split(' ')
    if len(sc) < 2: continue
    inner, parent = sc[-1], sc[-2]
    if inner.startswith(('source.', 'text.', 'vim.')) or parent.startswith(('source.', 'text.', 'vim.')): continue
    g0 = r['vim_trans'] or 'None'
    mq[(parent, inner)][g0 if (g0 in STD or g0 in EXTRA_OK) else 'None'] += int(r['chars'])
by = collections.defaultdict(collections.Counter)
for inner, c_all in m_all.items():
    if inner.startswith(('source.', 'text.', 'vim.')): continue
    parts = inner.split('.')
    for k in range(1, len(parts) + 1):
        c = m.get(inner, {}) if k == len(parts) else c_all    # der Scope selbst: ohne Codeblöcke; Eltern: wie bisher
        for g, n in c.items(): by['.'.join(parts[:k])][g] += n

def style(b, i, u):
    return ' '.join(s for s, f in (('bold', b), ('italic', i), ('underline', u)) if f)

def rule(label, scope, g):
    if g == 'None' or g not in G:
        return {'name': label, 'scope': scope, 'settings': {'foreground': NFG, 'fontStyle': ''}}
    fg, bg, b, i, u = eff(g, NFG)
    s = {'foreground': fg, 'fontStyle': style(b, i, u)}
    return {'name': label, 'scope': scope, 'settings': s}

rules = []
for scope in sorted(by):
    rules.append(rule(by[scope].most_common(1)[0][0], scope, by[scope].most_common(1)[0][0]))
QMIN = 2
for (parent, inner), c in sorted(mq.items()):
    (g, n), = c.most_common(1)
    if n < QMIN or n < 0.99 * sum(c.values()): continue      # eindeutig und ausreichend belegt
    gg = by[inner].most_common(1)[0][0] if by.get(inner) else None
    if g == gg: continue
    rules.append(rule(g, parent + ' ' + inner, g))
    print('qualifiziert:', parent, inner, '->', g, n, file=sys.stderr)
USED = set(g for c in m.values() for g in c if g in EXTRA_OK)
if _os.environ.get('GSTD'):
    USED |= set(l.rstrip('\n').split('\t')[1] for l in open(_os.environ['GSTD']) if l.strip()) & EXTRA_OK
for g in list(STD) + sorted(USED):
    rules.append(rule('vim ' + g, 'vim.' + g, g))
import os as _os
if _os.environ.get('LANGDUMP') and _os.environ.get('GSTD'):
    nsub = 0
    for line in open(_os.environ['GSTD']):
        vg, std = line.rstrip('\n').split('\t')
        if vg not in LD or std not in G: continue
        a = eff(vg if vg in G else 'lang:' + vg, NFG); b = eff(std, NFG)
        if (a[0] or NFG, a[2], a[3], a[4]) != (b[0] or NFG, b[2], b[3], b[4]):
            rules.append(rule(vg, 'vim.%s.%s' % (std, vg), vg if vg in G else 'lang:' + vg)); nsub += 1
    print('Sprachgruppen-Regeln:', nsub, file=sys.stderr)
rules.append(rule('vim Normal', 'vim.Normal', 'None'))
_ex = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'extra_rules.json')
if _os.path.exists(_ex):
    for e in json.load(open(_ex)):
        if 'fontStyle' in e:   # feste Darstellung: Vordergrundfarbe des Editors, nur Schriftstil
            rules.append({'name': e.get('name', e['scope']), 'scope': e['scope'], 'settings': {'foreground': NFG, 'fontStyle': e['fontStyle']}})
        else:
            rules.append(rule(e['group'], e['scope'], e['group']))
rules.append({'name': 'vim.Todo.bg', 'scope': 'vim.Todo', 'settings': rule('', '', 'Todo')['settings']})
rules.pop()  # (Platzhalter, nicht nötig)

# ---- UI: Workbench = "Dark (Visual Studio)" bzw. "Light (Visual Studio)"; nur der Editorbereich kommt von Vim
import os
HERE = os.path.dirname(os.path.abspath(__file__))
def strip_jsonc(t):
    out = []; i = 0; ins = False
    while i < len(t):
        c = t[i]
        if ins:
            out.append(c)
            if c == '\\': out.append(t[i + 1]); i += 1
            elif c == '"': ins = False
        elif c == '"': ins = True; out.append(c)
        elif t.startswith('//', i):
            while i < len(t) and t[i] != '\n': i += 1
            continue
        elif t.startswith('/*', i): i = t.index('*/', i) + 1
        else: out.append(c)
        i += 1
    return re.sub(r',(\s*[}\]])', r'\1', ''.join(out))
import re
BASE = json.loads(strip_jsonc(open(os.path.join(HERE, '..', 'data', 'ui-base', 'dark_vs.json' if dark else 'light_vs.json')).read()))['colors']
# Vom Vim-Editorbereich überschrieben bzw. unerwünscht aus der Basis
for k in ('editor.background', 'editor.foreground', 'editor.inactiveSelectionBackground', 'editor.selectionHighlightBackground'):
    BASE.pop(k, None)

def lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(c)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def contrast(a, b):
    la, lb = lum(a), lum(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)
def over(c, a, base):   # Farbe c mit Deckkraft a auf base
    return blend(base, c, a)

def fgo(g): return eff(g)[0] if g in G else None
def bgo(g): return eff(g)[1] if g in G else None
srch = bgo('Search'); isrch = bgo('IncSearch') or bgo('CurSearch'); fold = bgo('Folded')
cand = {  # Schlüssel: (Farbe, Deckkraft oder None) -- Hintergründe werden auf Lesbarkeit mit dem Editor-Vordergrund geprüft
 'editor.lineHighlightBackground': (bgo('CursorLine'), None),
 'editor.selectionBackground': (bgo('Visual'), None),
 'editorBracketMatch.background': (bgo('MatchParen'), None),
 'editor.findMatchBackground': (isrch, None),
 'editor.findMatchHighlightBackground': (srch, 0.6),
 'editor.foldBackground': (fold, 0.5),
}
colors = dict(BASE)
colors['editor.background'] = NBG
colors['editor.foreground'] = NFG
# VS Code färbt Klammerpaare selbst (Bracket Pair Colorization); Vim tut das nicht -> alle Ebenen in Editor-Schriftfarbe
dropped = []
for k, (c, a) in cand.items():
    if not c: continue
    eff_c = over(c, a, NBG) if a else c
    if contrast(eff_c, NFG) < 3.0:
        dropped.append(k); continue
    colors[k] = c + ('%02x' % round(a * 255) if a else '')
simple = {
 'editorCursor.foreground': bgo('Cursor'),
 'editorLineNumber.foreground': fgo('LineNr'),
 'editorLineNumber.activeForeground': fgo('CursorLineNr'),
 'editorWhitespace.foreground': fgo('Whitespace') or fgo('NonText'),
 'editorRuler.foreground': bgo('ColorColumn'),
 'editorBracketMatch.border': fgo('MatchParen'),
 'editorError.foreground': fgo('ErrorMsg') or bgo('ErrorMsg'),
 'editorWarning.foreground': fgo('WarningMsg'),
}
for k, v in simple.items():
    if v: colors[k] = v
if dropped and os.environ.get('MKDEBUG'): print(name, 'wegen Kontrast ausgelassen:', dropped, file=sys.stderr)
theme = {'name': name, 'type': 'dark' if dark else 'light', 'colors': colors, 'tokenColors': rules}
json.dump(theme, open(out, 'w'), indent=1)
