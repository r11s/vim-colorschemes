# python3 gen_inject.py <groups,komma> <ausgabeordner>
# Wörter je Sprache aus den Vim-Läufen (Wort -> Standardgruppe) -> Injection-Grammatiken
import csv, json, sys, os, collections
VD = os.environ.get('VD', '/tmp/vd')       # Arbeitsverzeichnis (Zwischenstände, Beispielprojekte)
groups = set(sys.argv[1].split(',')) if sys.argv[1] != 'ALL' else None
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
W = VD + '/words/gen/'
L = {'go': ('source.go', 'go'), 'python': ('source.python', 'py'), 'c': ('source.c', 'c'), 'java': ('source.java', 'java'), 'javascript': ('source.js', 'js')}
info = {}
for lang, (scope, ext) in L.items():
    lines = open(f'{W}{lang}.{ext}', encoding='utf-8').read().split('\n')
    by = collections.defaultdict(set)
    for r in csv.reader(open(f'{W}{lang}.el.std.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
        if len(r) < 5 or r[3] == '#END': continue
        word = lines[int(r[0]) - 1].strip(); std = r[4]
        if std in ('None', '', 'Normal') or std.startswith(lang) or not word.isidentifier(): continue
        if groups is None or std in groups: by[std].add(word)
    pats = []
    for std, ws in sorted(by.items()):
        ws = sorted(ws, key=lambda w: (-len(w), w))
        pats.append({'match': r'\b(?:' + '|'.join(ws) + r')\b', 'name': f'vim.{std}'})
    g = {'scopeName': f'vim.injection.{lang}', 'injectionSelector': f'L:{scope} -comment -string', 'patterns': pats}
    json.dump(g, open(f'{out}/{lang}.json', 'w'), indent=1)
    info[scope] = [f'vim.injection.{lang}']
    if lang == 'go':
        esc = {'scopeName': 'vim.injection.go-rune', 'injectionSelector': 'L:source.go string.quoted.rune',
               'patterns': [{'match': r"\\(?:[abfnrtv\\'\"]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|[0-7]{3})", 'name': 'vim.Special'}]}
        json.dump(esc, open(f'{out}/go-rune.json', 'w'), indent=1)
        info[scope].append('vim.injection.go-rune')
    print(lang, sum(len(v) for v in by.values()), 'Wörter in', len(pats), 'Gruppen')
json.dump(info, open(f'{out}/index.json', 'w'))
