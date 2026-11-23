#!/usr/bin/env python3
# mkpairs.py <variant: big|orig> <out>  : baut pairs-Datei mit train(big) oder train.orig; Wörter-/Kontextzeilen kommen aus pairs_B9
import sys, subprocess, json, os
var, out = sys.argv[1:3]
rest = [x for x in open('/tmp/tm/pairs_B9.tsv') if '/train\t' not in x.split('\t')[0]+'\t']
hdr = [x for x in rest if x.startswith('lang\t')]
rest = [x for x in rest if not x.startswith('lang\t')]
lines = hdr + rest
for l in open('/tmp/vd/lang/list.txt'):
    lang, ext, syn, scope = l.split()
    base = f'/tmp/vd/lang/files/{lang}.train.{ext}'
    src = base + '.orig' if (var == 'orig' and os.path.exists(base + '.orig')) else base
    std = f'/tmp/vd/lang/files/{lang}.train.{var}.std.tsv'
    env = dict(os.environ, CS='elflord', FILE=src, LANG_SYN=syn, OUT=std)
    subprocess.run(['timeout', '120', '/tmp/vim92/bin/vim', '-u', 'NONE', '-es', '-S', '/tmp/vd/ctx/runs3.vim'], env=env, stdin=subprocess.DEVNULL)
    jf = f'/tmp/jobs_{lang}.json'
    json.dump([{'lang': lang + '/train', 'scope': scope, 'src': src, 'runs': std}], open(jf, 'w'))
    subprocess.run(['node', 'pairs.js', jf, f'/tmp/pr_{lang}.tsv'], cwd='/tmp/tm', env=dict(os.environ, INJ='/tmp/tm/inj_B10'), stdout=subprocess.DEVNULL)
    lines += [x for x in open(f'/tmp/pr_{lang}.tsv') if not x.startswith('lang\t')]
open(out, 'w').write(''.join(lines))
print(out, len(lines))
