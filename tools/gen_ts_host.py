# python3 gen_ts_host.py [Ausgabedatei]
# Vims TypeScript-Syntax (typescriptcommon.vim, Block typescript_host_keyword) kennt viele eingebaute Namen:
#  - globale Namen (console, Math, Date, Error, ...)            -> Gruppe typescriptGlobal usw. (Structure)
#  - Member nach dem Punkt (Math.floor, console.log, x.toFixed)  -> Gruppen typescriptMathStaticMethod usw. (Keyword)
# Daraus entsteht eine Injection-Grammatik mit L-Priorität (sonst gewinnt die TextMate-Grammatik bei gleichem Start).
import re, os, json, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
RT92 = os.environ.get('RT92') or os.path.join(HERE, '..', 'rt92')
src = os.path.join(RT92, 'syntax', 'shared', 'typescriptcommon.vim')
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'extra_inject', 'typescript-host.json')
STD = {'Structure', 'Keyword', 'Statement', 'Type', 'Function', 'Constant', 'Special', 'Identifier'}
L = open(src, encoding='utf-8').read().split('\n')
s = next(i for i, l in enumerate(L) if 'typescript_host_keyword' in l and l.startswith('if'))
e = next(i for i in range(s, len(L)) if L[i].startswith('endif'))
block = L[s + 1:e]
words = collections.defaultdict(list); contained = {}; cin = {}; link = {}; props = set(); objs = collections.defaultdict(list); dots = {}
for l in block:
    m = re.match(r'\s*syntax keyword (\w+)\s+(.*)', l)
    if m:
        g, rest = m.groups(); ws = []; ng = []
        for t in rest.split():
            if t == 'contained': contained[g] = True
            elif t.startswith('containedin='): cin[g] = True
            elif t.startswith('nextgroup='): ng = t[10:].split(',')
            elif t in ('skipwhite', 'skipempty', 'skipnl') or t.startswith('contains='): pass
            elif re.match(r'^[A-Za-z_$][\w$]*$', t): ws.append(t)
        words[g] += ws
        for n in ng:
            if re.match(r'typescriptGlobal\w+Dot$', n): objs[n] += ws
        continue
    m = re.match(r'\s*syntax match\s+(typescriptGlobal\w+Dot)\s+/\\\./.*nextgroup=(\S+)', l)
    if m: dots[m.group(1)] = [x for x in m.group(2).split(',') if x != 'typescriptProp']; continue
    m = re.match(r'\s*syntax cluster props add=(\S+)', l)
    if m: props.update(m.group(1).split(','))
    m = re.match(r'\s*hi(?:ghlight)? def(?:ault)? link (\w+) (\w+)', l)
    if m: link[m.group(1)] = m.group(2)
def alt(ws): return '|'.join(sorted(set(ws), key=lambda w: (-len(w), w)))
pats = []; names = []
glob = collections.defaultdict(list); prop = collections.defaultdict(list)   # Standardgruppe -> Wörter
# 1. globale Namen
for g in sorted(words):
    if cin.get(g) and not contained.get(g) and link.get(g) in STD:
        glob[link[g]] += words[g]
# 2. Member nach bestimmtem Objekt (Math.floor, console.log, ...)
for d, mg in sorted(dots.items()):
    o = objs.get(d)
    if not o: continue
    for g in mg:
        if g in words and link.get(g) in STD:
            behind = '|'.join(sorted({r'\b' + x + r'\.' for x in o}, key=lambda x: (-len(x), x)))
            pats.append({'match': '(?<=' + behind + ')(?:' + alt(words[g]) + r')(?![\w$])', 'name': f'vim.{link[g]}.{g}'}); names.append((g, link[g]))
# 3. Member nach beliebigem Objekt (x.toFixed, a.push, ...)
for g in sorted(props):
    if g in words and link.get(g) in STD and contained.get(g):
        prop[link[g]] += words[g]
# Je Standardgruppe ein Muster statt ~90: gleiche Farbe, deutlich schnellere Einfärbung
for std, ws in sorted(glob.items()):
    pats.insert(0, {'match': r'(?<![\w$.])(?:' + alt(ws) + r')(?![\w$])', 'name': f'vim.{std}.typescriptGlobal'}); names.append(('typescriptGlobal', std))
for std, ws in sorted(prop.items()):
    pats.append({'match': r'(?<=\.)(?:' + alt(ws) + r')(?![\w$])', 'name': f'vim.{std}.typescriptProp'}); names.append(('typescriptProp', std))
    # Zugriff ohne Aufruf (this.name, x.length): die TextMate-Regel beginnt schon beim Punkt und gewinnt sonst -> Muster beginnt ebenfalls beim Punkt
    pats.append({'match': r'(\??\.)(' + alt(ws) + r')(?![\w$]|\s*\()', 'captures': {'1': {'name': 'punctuation.accessor.ts'}, '2': {'name': f'vim.{std}.typescriptProp'}}})
# Strings ausgenommen, Ausdrücke in Template-Strings (${...}) nicht
SELECTOR = 'L:source.ts -comment -(string -meta.embedded)'
# 4. einzelne Schlüsselwörter außerhalb des Host-Blocks, deren Farbe sich vom TextMate-Scope unterscheidet
#    (abstract: gleiches Scope wie public/static, in Vim aber Special). Folgt ein Leerraum, bleibt die Klassen-/Methodenregel der Grammatik erhalten.
for g, in (('typescriptAbstract',),):
    ws = []; std = None
    for l in L:
        m = re.match(r'\s*syntax keyword ' + g + r'\s+(.*)', l)
        if m: ws += [t for t in m.group(1).split() if re.match(r'^[A-Za-z_$][\w$]*$', t) and t not in ('contained',)]
        m = re.match(r'\s*hi(?:ghlight)? def(?:ault)? link ' + g + r'\s+(\w+)', l)
        if m: std = m.group(1)
    if ws and std in STD:
        pats.append({'match': r'(?<![\w$.])(?:' + alt(ws) + r')(?=\s)', 'name': f'vim.{std}.{g}'}); names.append((g, std))
g = {'scopeName': 'vim.injection.typescript-host', 'injectionSelector': SELECTOR, 'patterns': pats}
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(g, open(out, 'w', encoding='utf-8'), indent=1)
print(len(pats), 'Muster,', len(set(names)), 'Gruppen ->', out, file=sys.stderr)
