set nocp
set rtp^=/tmp/vd/rt92
set columns=200
syntax on
execute 'edit ' . $FILE
execute 'set syntax=' . $LANG_SYN
syntax sync fromstart
let res = []
for l in range(1, line('$'))
  let id = synID(l, match(getline(l), '\S') + 1, 1)
  call add(res, l . "\t" . synIDattr(id, 'name') . "\t" . synIDattr(synIDtrans(id), 'name'))
endfor
call writefile(res, $OUT)
qa!
