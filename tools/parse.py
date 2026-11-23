import re, json, sys, glob, os
FLAGS = re.compile(r'^(contained|skipwhite|skipnl|skipempty|transparent|display|fold|oneline|keepend|extend|excludenl|concealends|conceal|containedin=\S*|nextgroup=\S*|contains=\S*|cchar=\S*|group[ht]ere=\S*)$')
out = {}
for f in sorted(glob.glob('raw_*.txt')):
    lang = f[4:-4]
    groups = {}
    cur = None
    for line in open(f, encoding='utf-8', errors='replace'):
        line = line.rstrip('\n')
        m = re.match(r'^(\S+)\s+xxx\s?(.*)$', line)
        if m:
            cur = m.group(1); groups.setdefault(cur, {'words': [], 'link': None})
            rest = m.group(2)
        elif line.startswith(' ') and cur:
            rest = line.strip()
            if rest.startswith('links to '):
                groups[cur]['link'] = rest[9:].strip(); continue
        else:
            continue
        mm = re.match(r'^match /(.*)/(\s.*)?$', rest)
        if mm:
            pat, fl = mm.group(1), (mm.group(2) or '')
            for alt in re.finditer(r'\\<\\%?\((\w+(?:\\\|\w+)*)\\\)\\>', pat):
                for w in alt.group(1).split('\\|'):
                    groups[cur]['words'].append((w, ['contained'] if 'contained' in fl.split() else []))
            m2 = re.fullmatch(r'\\<(\w+)\\>', pat)
            if m2: groups[cur]['words'].append((m2.group(1), ['contained'] if 'contained' in fl.split() else []))
            continue
        if re.match(r'^(start=|end=|skip=|matchgroup=|cluster)', rest) or rest == '' : continue
        flags = set(); toks = rest.split()
        for t in toks:
            if FLAGS.match(t): flags.add(t)
            else: groups[cur]['words'].append((t, sorted(flags)))
    out[lang] = groups
    n = sum(len(g['words']) for g in groups.values())
    print(lang, len(groups), 'groups', n, 'words')
json.dump(out, open('words.json', 'w'), indent=1)
