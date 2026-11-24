set nocp
" Runtime von Vim 9.2: $RT92, sonst rt92/ im Repo, sonst /tmp/vd/rt92
let s:repo = expand('<sfile>:p:h:h')
let s:rt = !empty($RT92) ? $RT92 : (isdirectory(s:repo . '/rt92') ? s:repo . '/rt92' : '/tmp/vd/rt92')
execute 'set rtp^=' . fnameescape(s:rt)
set columns=20000
syntax on
execute 'set syntax=' . $LANG_SYN
execute 'redir! > ' . fnameescape((empty($VD) ? '/tmp/vd' : $VD) . '/words/raw_' . $LANG_SYN . '.txt')
silent syntax list
redir END
qa!
