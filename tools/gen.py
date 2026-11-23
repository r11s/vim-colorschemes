import json, re
EXT = dict(c='c', cpp='cpp', cs='cs', go='go', html='html', java='java', javascript='js', kotlin='kt', pascal='pas', python='py', ruby='rb', xml='xml', cobol='cob', typescript='ts', php='php', rust='rs', sh='sh', css='css', json='json', yaml='yaml', markdown='md', sql='sql', lua='lua', vim='vim', ps1='ps1', dosbatch='bat', swift='swift', dart='dart', scala='scala', perl='pl', r='r', dockerfile='dockerfile', make='mk', toml='toml', dosini='ini', diff='diff', scss='scss', less='less')
d = json.load(open('words.json'))
idx = {}
for lang, groups in d.items():
    rows = []; seen = set(); skipped = []
    for g, info in groups.items():
        for w, fl in info['words']:
            if 'contained' in fl or not re.match(r'^[A-Za-z_]\w*$', w): skipped.append((w,g,fl)); continue
            if (w, g) in seen: continue
            seen.add((w, g)); rows.append((w, g, ','.join(fl)))
    fn = f'gen/{lang}.{EXT[lang]}'
    with open(fn, 'w', newline='\n') as fh:
        for w, g, fl in rows: fh.write(('       ' if lang=='cobol' else '') + w + '\n')
    with open(f'gen/{lang}.meta.tsv', 'w') as fh:
        for i, (w, g, fl) in enumerate(rows, 1): fh.write(f'{i}\t{w}\t{g}\t{fl}\n')
    print(lang, len(rows), 'Wörter,', len(skipped), 'übersprungen (contained/Sonderzeichen)')
