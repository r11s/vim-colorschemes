#!/bin/bash
# retrain.sh <lang>  : Vim-Referenz + pairs der train-Datei neu, in pairs_B9.tsv ersetzen (Backup .bak)
VD=${VD:-/tmp/vd}; TM=${TM:-/tmp/tm}; VIM=${VIM:-/tmp/vim92/bin/vim}   # Pfade, per Umgebungsvariable änderbar
l=$1
read lang ext syn scope < <(grep "^$l " $VD/lang/list.txt)
F=$VD/lang/files/$lang.train.$ext
CS=elflord FILE=$F LANG_SYN=$syn OUT=$VD/lang/files/$lang.train.std.tsv timeout 120 $VIM -u NONE -es -S $VD/ctx/runs3.vim </dev/null
python3 - $lang $scope $F <<PY
import json,sys
l,sc,f=sys.argv[1:4]
json.dump([{'lang':l+'/train','scope':sc,'src':f,'runs':f.rsplit('.',1)[0]+'.std.tsv'}],open('/tmp/jobs_re.json','w'))
PY
cd $TM && INJ=${INJ:-$TM/inj_B10} node pairs.js /tmp/jobs_re.json /tmp/pairs_re.tsv
cp $TM/pairs_B9.tsv $TM/pairs_B9.tsv.bak
python3 - $lang <<PY
import sys
l=sys.argv[1]
old=[x for x in open('$TM/pairs_B9.tsv') if not x.startswith(l+'/train\t')]
new=[x for x in open("/tmp/pairs_re.tsv") if not x.startswith("lang\t")]
open('$TM/pairs_B9.tsv','w').write(''.join(old+new))
print(len(new),'neue Zeilen')
PY
