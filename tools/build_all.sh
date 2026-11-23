#!/bin/bash
# build_all.sh <pairs.tsv> <outdir>
cd /tmp/vd/mk2
for f in themes/vim-*-color-theme.json; do
  b=$(basename $f); read name type < <(python3 -c "import json,sys;j=json.load(open('$f'));print(j['name'].replace(' ','_'),j['type'])")
  name=${name//_/ }
  s=${b#vim-}; s=${s%-color-theme.json}; s=${s%-dark}; s=${s%-light}
  LANGDUMP=/tmp/vd/schemes/lang/$s.$type.json GSTD=${GSTD:-/dev/null} python3 tools/mktheme.py /tmp/vd/schemes/$s.$type.json $1 $2/$b "$name" 2>/dev/null || echo FEHLER $b
done
