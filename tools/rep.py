import os
import csv, collections
VD = os.environ.get('VD', '/tmp/vd')       # Arbeitsverzeichnis (Zwischenstände, Beispielprojekte)
for l in 'c cpp go java javascript kotlin pascal python cobol'.split():
    meta = {int(r[0]): r for r in csv.reader(open(f'{VD}/words/gen/{l}.meta.tsv'), delimiter='\t')}
    ok = miss = other = 0; ex = collections.Counter(); mi = collections.Counter()
    for r in csv.reader(open(f'{VD}/words/gen/{l}.vim.tsv'), delimiter='\t'):
        i = int(r[0]); name = r[1] if len(r) > 1 else ''
        decl = meta[i][2]
        if name == decl: ok += 1
        elif name == '': miss += 1; mi[decl]+=1
        else: other += 1; ex[(decl,name)] += 1
    print(f'{l:11} {len(meta):4} Wörter: {ok} gleiche Gruppe, {miss} ohne Treffer, {other} andere Gruppe', dict(ex.most_common(3)), dict(mi.most_common(2)))
