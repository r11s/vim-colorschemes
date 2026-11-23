set nocp
set rtp^=/tmp/vd/rt92
set termguicolors
set t_Co=256
syntax on
execute 'set background=' . $BG
execute 'colorscheme ' . $CS
enew
for ft in ['go', 'python', 'c', 'java', 'javascript', 'rust', 'cpp', 'cs', 'typescript', 'ruby', 'sh', 'css', 'json', 'yaml', 'markdown', 'sql', 'lua', 'vim', 'ps1', 'dosbatch', 'perl', 'dosini', 'toml', 'diff', 'scss', 'less', 'html', 'xml', 'make', 'php', 'dockerfile', 'cobol', 'pascal', 'swift', 'dart', 'kotlin', 'scala', 'r']
  execute 'set syntax=' . ft
endfor
let out = {}
for n in readfile($NAMES)
  let id = hlID(n)
  if id == 0 | continue | endif
  let t = synIDtrans(id)
  let d = {'trans': synIDattr(t, 'name'), 'fg': synIDattr(t, 'fg#', 'gui'), 'bg': synIDattr(t, 'bg#', 'gui')}
  for a in ['bold', 'italic', 'underline', 'undercurl', 'strikethrough', 'reverse']
    let d[a] = synIDattr(t, a, 'gui') == '1' ? 1 : 0
  endfor
  let out[n] = d
endfor
call writefile([json_encode(out)], $OUT)
qa!
