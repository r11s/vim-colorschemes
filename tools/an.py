import csv, collections, sys
rows = []
for r in csv.DictReader(open('pairs.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
    sp = r['tm_scopes'].split(' ')
    inner = sp[-1]
    rows.append((r['lang'].split('/')[0], r['lang'].split('/')[1], r['vim_trans'] or 'None', inner, int(r['chars']), r['vim_group']))
def fit(data):
    m = collections.defaultdict(collections.Counter)
    for lang, kind, tr, inner, n, g in data: m[(lang, inner)][tr] += n
    return {k: c.most_common(1)[0][0] for k, c in m.items()}, m
def acc(model, data):
    ok = tot = 0
    for lang, kind, tr, inner, n, g in data:
        tot += n
        p = model.get((lang, inner))
        if p == tr: ok += n
        elif p is None and False: pass
    return ok, tot
print('Sprache      Zeichen   in-Probe   Wörter->Kontext')
for lang in ['go', 'python', 'c', 'java', 'javascript']:
    d = [r for r in rows if r[0] == lang]; ctx = [r for r in d if r[1] == 'ctx']; wd = [r for r in d if r[1] == 'words']
    mall, _ = fit(d); ok, tot = acc(mall, ctx)
    mw, _ = fit(wd); ok2, tot2 = acc(mw, ctx)
    print(f'{lang:11} {tot:7}  {100*ok/tot:6.1f} %   {100*ok2/tot2:6.1f} %')
# Mehrdeutige Scopes im Kontext
for lang in ['go', 'python', 'c', 'java', 'javascript']:
    d = [r for r in rows if r[0] == lang]
    mall, m = fit(d)
    amb = []
    for (l, inner), c in m.items():
        if l != lang: continue
        tot = sum(c.values()); top = c.most_common(1)[0][1]
        if top < tot: amb.append((tot - top, inner, dict(c.most_common(3))))
    amb.sort(reverse=True)
    print(f'\n== {lang}: mehrdeutige Scopes (Zeichen, die das Mehrheitsurteil verfehlt)')
    for n, inner, c in amb[:8]: print(f'  {n:4} {inner:42} {c}')
