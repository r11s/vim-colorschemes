#!/bin/bash
# Pascal: keine Vim-Regeln; stattdessen Wirth-Darstellung (fett Schlüsselwörter, kursiv Bezeichner)
rm -rf /tmp/tm/inj_np && cp -r /tmp/tm/inj_B10 /tmp/tm/inj_np && rm /tmp/tm/inj_np/pascal.json /tmp/tm/inj_np/pascal-todo.json
python3 - <<'PY'
import json
d='/tmp/tm/inj_np/'
idx=json.load(open(d+'index.json')); idx.pop('source.pascal')
idx['source.pascal']=['vim.injection.pascal-wirth']
json.dump(idx,open(d+'index.json','w'))
json.dump({'scopeName':'vim.injection.pascal-wirth','injectionSelector':'source.pascal -comment -string','patterns':[{'match':r'[A-Za-z_]\w*','name':'wirth.identifier.pascal'}]},open(d+'pascal-wirth.json','w'),indent=1)
open(d+'groups_std.tsv','w').writelines(l for l in open('/tmp/tm/inj_B10/groups_std.tsv') if not l.startswith('pascal'))
open('/tmp/tm/pairs_np.tsv','w').writelines(x for x in open('/tmp/tm/pairs_mix.tsv') if not x.startswith('pascal/'))
PY
