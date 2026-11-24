set nocp
" Runtime von Vim 9.2: $RT92, sonst rt92/ im Repo, sonst /tmp/vd/rt92
let s:repo = expand('<sfile>:p:h:h')
let s:rt = !empty($RT92) ? $RT92 : (isdirectory(s:repo . '/rt92') ? s:repo . '/rt92' : '/tmp/vd/rt92')
execute 'set rtp^=' . fnameescape(s:rt)
set columns=200
set background=dark
set termguicolors
set t_Co=256
execute 'colorscheme ' . $CS
let c_comment_strings=1
syntax on
execute 'edit ' . $FILE
execute 'set syntax=' . $LANG_SYN
syntax sync fromstart
let std = {}
for n in split('Comment Constant String Character Number Boolean Float Identifier Function Statement Conditional Repeat Label Operator Keyword Exception PreProc Include Define Macro PreCondit Type StorageClass Structure Typedef Special SpecialChar Tag Delimiter SpecialComment Debug Underlined Ignore Error Todo Normal', ' ')
  let std[n] = 1
endfor
let nf = synIDattr(synIDtrans(hlID('Normal')), 'fg#', 'gui')
function! StdOf(nm) abort
  let n = a:nm
  let i = 0
  while i < 20
    if has_key(g:std, n) | return n | endif
    redir => o
    silent! execute 'hi ' . n
    redir END
    let m = matchlist(o, 'links to \(\w\+\)')
    if empty(m) | return n | endif
    let n = m[1]
    let i += 1
  endwhile
  return n
endfunction
let cache = {}
let res = []
for l in range(1, line('$'))
  let t = getline(l)
  let n = strlen(t)
  let c = 1
  let start = 1
  let prev = ''
  let prevS = ''
  let prevF = ''
  while c <= n + 1
    if c <= n
      let id = synID(l, c, 1)
      let nm = synIDattr(id, 'name')
      if nm == ''
        let sd = 'None'
        let fg = nf
      else
        if !has_key(cache, nm) | let cache[nm] = StdOf(nm) | endif
        let sd = cache[nm]
        let fg = synIDattr(synIDtrans(id), 'fg#', 'gui')
        if fg == '' | let fg = nf | endif
      endif
    else
      let nm = '#END'
      let sd = ''
      let fg = ''
    endif
    if c > 1 && (nm != prev || sd != prevS || fg != prevF)
      call add(res, l . "\t" . start . "\t" . (c - 1) . "\t" . prev . "\t" . prevS . "\t" . prevF)
      let start = c
    endif
    let prev = nm
    let prevS = sd
    let prevF = fg
    let c += 1
  endwhile
endfor
call writefile(res, $OUT)
" Standardpalette des Schemas
let pal = []
for n in keys(std)
  let f = synIDattr(synIDtrans(hlID(n)), 'fg#', 'gui')
  let b = synIDattr(synIDtrans(hlID(n)), 'bold')
  call add(pal, n . "\t" . f . "\t" . b)
endfor
call writefile(sort(pal), $OUT . '.pal')
qa!
