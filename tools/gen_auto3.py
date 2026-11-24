import os
import csv, collections, json, sys, glob
VD = os.environ.get('VD', '/tmp/vd')       # Arbeitsverzeichnis (Zwischenstände, Beispielprojekte)
pairs, out, colname = sys.argv[1], sys.argv[2], sys.argv[3]
# Palette: wirksame Gruppe -> Farbe aus den Vim-Läufen
pal = {}
for r in csv.reader(open(VD + '/ctx/go.go.' + colname + '.std.tsv.pal'), delimiter='\t', quoting=csv.QUOTE_NONE):
    pal[r[0]] = r[1]
fg = pal['Normal']
STD = set(pal)
m = collections.defaultdict(collections.Counter)
for r in csv.DictReader(open(pairs), delimiter='\t', quoting=csv.QUOTE_NONE):
    inner = r['tm_scopes'].split(' ')[-1]
    g0 = r['vim_trans'] or 'None'; m[(r['lang'].split('/')[0], inner)][g0 if g0 in STD and g0 != 'Normal' else 'None'] += int(r['chars'])
# Scope-Präfixe: jeder Scope zählt für alle seine Präfixe (Rückfall für ungesehene Scopes)
by = collections.defaultdict(collections.Counter)
for (lang, inner), c in m.items():
    if inner.startswith('source.') or inner.startswith('text.'): continue
    parts = inner.split('.')
    for k in range(1, len(parts) + 1):
        p = '.'.join(parts[:k])
        for g, n in c.items(): by[p][g] += n
rules = []
for scope, c in sorted(by.items()):
    g = c.most_common(1)[0][0]
    color = pal.get(g, fg) if g != 'None' else fg
    rules.append({'name': g, 'scope': scope, 'settings': {'foreground': color}})
theme = {'name': 'auto', 'type': 'dark', 'colors': {'editor.background': '#000000', 'editor.foreground': fg}, 'tokenColors': rules}
json.dump(theme, open(out, 'w'), indent=1)
print(len(rules), 'Regeln, Vordergrund', fg, 'Gruppen:', {g: pal.get(g) for g in sorted(set(r['name'] for r in rules))})
