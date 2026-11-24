set nocp
" Runtime von Vim 9.2: $RT92, sonst rt92/ im Repo, sonst /tmp/vd/rt92
let s:repo = expand('<sfile>:p:h:h')
let s:rt = !empty($RT92) ? $RT92 : (isdirectory(s:repo . '/rt92') ? s:repo . '/rt92' : '/tmp/vd/rt92')
execute 'set rtp^=' . fnameescape(s:rt)
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
