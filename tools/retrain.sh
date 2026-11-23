#!/bin/bash
# retrain.sh <lang>  : Vim-Referenz + pairs der train-Datei neu, in pairs_B9.tsv ersetzen (Backup .bak)
l=$1
read lang ext syn scope < <(grep "^$l " /tmp/vd/lang/list.txt)
F=/tmp/vd/lang/files/$lang.train.$ext
CS=elflord FILE=$F LANG_SYN=$syn OUT=/tmp/vd/lang/files/$lang.train.std.tsv timeout 120 /tmp/vim92/bin/vim -u NONE -es -S /tmp/vd/ctx/runs3.vim </dev/null
python3 - $lang $scope $F <<PY
import json,sys
l,sc,f=sys.argv[1:4]
json.dump([{'lang':l+'/train','scope':sc,'src':f,'runs':f.rsplit('.',1)[0]+'.std.tsv'}],open('/tmp/jobs_re.json','w'))
PY
cd /tmp/tm && INJ=${INJ:-/tmp/tm/inj_B10} node pairs.js /tmp/jobs_re.json /tmp/pairs_re.tsv
cp /tmp/tm/pairs_B9.tsv /tmp/tm/pairs_B9.tsv.bak
python3 - $lang <<PY
import sys
l=sys.argv[1]
old=[x for x in open('/tmp/tm/pairs_B9.tsv') if not x.startswith(l+'/train\t')]
new=[x for x in open("/tmp/pairs_re.tsv") if not x.startswith("lang\t")]
open('/tmp/tm/pairs_B9.tsv','w').write(''.join(old+new))
print(len(new),'neue Zeilen')
PY
