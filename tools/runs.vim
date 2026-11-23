set nocp
set rtp^=/tmp/vd/rt92
set columns=200
syntax on
execute 'edit ' . $FILE
execute 'set syntax=' . $LANG_SYN
syntax sync fromstart
let res = []
for l in range(1, line('$'))
  let t = getline(l)
  let n = strlen(t)
  let c = 1
  let start = 1
  let prev = ''
  let prevT = ''
  while c <= n + 1
    if c <= n
      let id = synID(l, c, 1)
      let nm = synIDattr(id, 'name')
      let tr = synIDattr(synIDtrans(id), 'name')
    else
      let nm = '#END'
      let tr = ''
    endif
    if c > 1 && (nm != prev || tr != prevT)
      call add(res, l . "\t" . start . "\t" . (c - 1) . "\t" . prev . "\t" . prevT . "\t" . substitute(strpart(t, start - 1, c - start), "\t", '\\t', 'g'))
      let start = c
    endif
    let prev = nm
    let prevT = tr
    let c += 1
  endwhile
endfor
call writefile(res, $OUT)
qa!
