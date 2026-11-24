#!/bin/bash
# Pascal: keine Vim-Regeln; stattdessen Wirth-Darstellung (fett Schlüsselwörter, kursiv Bezeichner)
TM=${TM:-/tmp/tm}   # Pfad per Umgebungsvariable änderbar
rm -rf $TM/inj_np && cp -r $TM/inj_B10 $TM/inj_np && rm $TM/inj_np/pascal.json $TM/inj_np/pascal-todo.json
TM=$TM python3 - <<'PY'
import json, os
TM = os.environ['TM']
d=TM+'/inj_np/'
idx=json.load(open(d+'index.json')); idx.pop('source.pascal')
idx['source.pascal']=['vim.injection.pascal-wirth']
json.dump(idx,open(d+'index.json','w'))
json.dump({'scopeName':'vim.injection.pascal-wirth','injectionSelector':'source.pascal -comment -string','patterns':[{'match':r'[A-Za-z_]\w*','name':'wirth.identifier.pascal'}]},open(d+'pascal-wirth.json','w'),indent=1)
open(d+'groups_std.tsv','w').writelines(l for l in open(TM+'/inj_B10/groups_std.tsv') if not l.startswith('pascal'))
open(TM+'/pairs_np.tsv','w').writelines(x for x in open(TM+'/pairs_mix.tsv') if not x.startswith('pascal/'))
PY
