set nocp
set rtp^=/tmp/vd/rt92
set columns=20000
syntax on
execute 'set syntax=' . $LANG_SYN
redir! > /tmp/vd/words/raw_$LANG_SYN.txt
silent syntax list
redir END
qa!
