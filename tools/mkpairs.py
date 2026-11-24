#!/usr/bin/env python3
# mkpairs.py <variant: big|orig> <out>  : baut pairs-Datei mit train(big) oder train.orig; Wörter-/Kontextzeilen kommen aus pairs_B9
import sys, subprocess, json, os
VD = os.environ.get('VD', '/tmp/vd')       # Arbeitsverzeichnis (Zwischenstände, Beispielprojekte)
TM = os.environ.get('TM', '/tmp/tm')       # Verzeichnis mit pairs.js, node_modules, Injektionen
VIM = os.environ.get('VIM', '/tmp/vim92/bin/vim')
var, out = sys.argv[1:3]
rest = [x for x in open(TM + '/pairs_B9.tsv') if '/train\t' not in x.split('\t')[0]+'\t']
hdr = [x for x in rest if x.startswith('lang\t')]
rest = [x for x in rest if not x.startswith('lang\t')]
lines = hdr + rest
for l in open(VD + '/lang/list.txt'):
    lang, ext, syn, scope = l.split()
    base = f'{VD}/lang/files/{lang}.train.{ext}'
    src = base + '.orig' if (var == 'orig' and os.path.exists(base + '.orig')) else base
    std = f'{VD}/lang/files/{lang}.train.{var}.std.tsv'
    env = dict(os.environ, CS='elflord', FILE=src, LANG_SYN=syn, OUT=std)
    subprocess.run(['timeout', '120', VIM, '-u', 'NONE', '-es', '-S', VD + '/ctx/runs3.vim'], env=env, stdin=subprocess.DEVNULL)
    jf = f'/tmp/jobs_{lang}.json'
    json.dump([{'lang': lang + '/train', 'scope': scope, 'src': src, 'runs': std}], open(jf, 'w'))
    subprocess.run(['node', 'pairs.js', jf, f'/tmp/pr_{lang}.tsv'], cwd=TM, env=dict(os.environ, INJ=TM + '/inj_B10'), stdout=subprocess.DEVNULL)
    lines += [x for x in open(f'/tmp/pr_{lang}.tsv') if not x.startswith('lang\t')]
open(out, 'w').write(''.join(lines))
print(out, len(lines))
