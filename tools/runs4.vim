set nocp
" Runtime von Vim 9.2: $RT92, sonst rt92/ im Repo, sonst /tmp/vd/rt92
let s:repo = expand('<sfile>:p:h:h')
let s:rt = !empty($RT92) ? $RT92 : (isdirectory(s:repo . '/rt92') ? s:repo . '/rt92' : '/tmp/vd/rt92')
execute 'set rtp^=' . fnameescape(s:rt)
set columns=200
execute 'set background=' . $BG
set termguicolors
set t_Co=256
let c_comment_strings=1
syntax on
execute 'colorscheme ' . $CS
execute 'edit ' . $FILE
execute 'set syntax=' . $LANG_SYN
syntax sync fromstart
let std = {}
for n in split('Comment Constant String Character Number Boolean Float Identifier Function Statement Conditional Repeat Label Operator Keyword Exception PreProc Include Define Macro PreCondit Type StorageClass Structure Typedef Special SpecialChar Tag Delimiter SpecialComment Debug Underlined Ignore Error Todo Normal', ' ')
  let std[n] = 1
endfor
let nf = synIDattr(synIDtrans(hlID('Normal')), 'fg#', 'gui')
if nf == '' | let nf = &background == 'dark' ? '#ffffff' : '#000000' | endif
let cache = {}
let res = []
for l in range(1, line('$'))
  let t = getline(l)
  let n = strlen(t)
  let c = 1
  let start = 1
  let prev = ''
  let prevF = ''
  while c <= n + 1
    if c <= n
      let id = synID(l, c, 1)
      let nm = synIDattr(id, 'name')
      if nm == ''
        let fg = nf
      else
        let t2 = synIDtrans(id)
        let fg = synIDattr(t2, 'fg#', 'gui')
        if synIDattr(t2, 'reverse', 'gui') == '1' | let fg = synIDattr(t2, 'bg#', 'gui') | endif
        if fg == '' | let fg = nf | endif
      endif
    else
      let nm = '#END'
      let fg = ''
    endif
    if c > 1 && (nm != prev || fg != prevF)
      call add(res, l . "\t" . start . "\t" . (c - 1) . "\t" . prev . "\t" . "" . "\t" . prevF)
      let start = c
    endif
    let prev = nm
    let prevF = fg
    let c += 1
  endwhile
endfor
call writefile(res, $OUT)
qa!
