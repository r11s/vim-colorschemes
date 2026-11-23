# python3 gen_words_all.py <inj_in> <inj_out>   (Wort-/Todo-Injektionen für alle weiteren Sprachen)
import csv, json, sys, os, re, collections, shutil
src, out = sys.argv[1], sys.argv[2]
shutil.copytree(src, out, dirs_exist_ok=True)
SPEC = [l.split() for l in open('/tmp/vd/lang/list.txt')]
W = '/tmp/vd/words/gen/'; UP = '/tmp/vd/lang/upper/'; RT = '/tmp/vd/rt92/syntax/'
index = json.load(open(f'{out}/index.json'))
groups = [l.rstrip('\n') for l in open(f'{out}/groups_std.tsv')]
GR = set(tuple(l.split('\t')) for l in groups if l)
def load(p):
    d = {}
    for r in csv.reader(open(p), delimiter='\t', quoting=csv.QUOTE_NONE):
        if len(r) >= 5 and r[3] != '#END': d.setdefault(int(r[0]), r)
    return d
for lang, ext, syn, scope in SPEC:
    if lang in ('go', 'python', 'c', 'java', 'javascript'): continue
    pats = []
    wf = f'{W}{lang}.{ext}'
    if os.path.exists(wf) and os.path.exists(f'{W}{lang}.el.std.tsv'):
        lines = open(wf, encoding='utf-8').read().split('\n')
        a = load(f'{W}{lang}.el.std.tsv'); b = load(f'{UP}{lang}.el.std.tsv') if os.path.exists(f'{UP}{lang}.el.std.tsv') else {}
        by = collections.defaultdict(set)
        for i, r in a.items():
            word = lines[i - 1].strip(); std, vg = r[4], r[3]
            if std in ('None', '', 'Normal') or not word.isidentifier(): continue
            ci = word != word.upper() and i in b and b[i][4] == std
            by[(std, vg, ci)].add(word)
        for (std, vg, ci), ws in sorted(by.items()):
            ws = sorted(ws, key=lambda w: (-len(w), w))
            if ci: ws = sorted({w.lower() for w in ws}, key=lambda w: (-len(w), w))
            pats.append({'match': ('(?i)' if ci else '') + r'\b(?:' + '|'.join(ws) + r')\b' + (r'(?!\s*\()' if vg == 'cssTagName' else ''), 'name': f'vim.{std}.{vg}'})
            GR.add((vg, std))
        NOL = ('typescript', 'sh', 'cobol')   # hier würde die L-Priorität TextMate-Strukturregeln zerstören
        g = {'scopeName': f'vim.injection.{lang}', 'injectionSelector': ('' if lang in NOL else 'L:') + f'{scope} -comment -string', 'patterns': pats}
        json.dump(g, open(f'{out}/{lang}.json', 'w'), indent=1)
        index.setdefault(scope, []).append(g['scopeName'])
    # Todo-Wörter aus der Vim-Syntaxdatei
    sf = RT + syn + '.vim'
    if os.path.exists(sf):
        for l in open(sf, encoding='utf-8', errors='replace'):
            m = re.match(r'\s*syn(?:tax)?\s+keyword\s+(\w*[Tt]odo\w*)\s+(.*)', l)
            if m:
                vg = m.group(1); ws = [w for w in m.group(2).split() if re.match(r'^[A-Z]\w+$', w) and w not in ('contained', 'containedin')]
                if ws:
                    name = f'{lang}-todo'
                    json.dump({'scopeName': f'vim.injection.{name}', 'injectionSelector': f'L:{scope} comment',
                               'patterns': [{'match': r'\b(?:' + '|'.join(sorted(ws, key=lambda w: (-len(w), w))) + r')\b', 'name': f'vim.Todo.{vg}'}]},
                              open(f'{out}/{name}.json', 'w'), indent=1)
                    index.setdefault(scope, []).append(f'vim.injection.{name}'); GR.add((vg, 'Todo'))
                break
json.dump(index, open(f'{out}/index.json', 'w'))
open(f'{out}/groups_std.tsv', 'w').write('\n'.join(f'{g}\t{s}' for g, s in sorted(GR)) + '\n')
print(len(index), 'Scopes;', len(GR), 'Gruppen')
