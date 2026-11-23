set nocp
set rtp^=/tmp/vd/rt92
set termguicolors
set t_Co=256
syntax on
execute 'set background=' . $BG
execute 'colorscheme ' . $CS
let grp = split('Normal NormalNC Cursor lCursor CursorIM CursorColumn CursorLine CursorLineNr LineNr LineNrAbove LineNrBelow SignColumn FoldColumn Folded ColorColumn Conceal Visual VisualNOS Search IncSearch CurSearch MatchParen NonText SpecialKey Whitespace EndOfBuffer StatusLine StatusLineNC StatusLineTerm StatusLineTermNC VertSplit WinSeparator WinBar WinBarNC TabLine TabLineSel TabLineFill Pmenu PmenuSel PmenuSbar PmenuThumb PmenuKind PmenuExtra WildMenu Directory Title ErrorMsg WarningMsg ModeMsg MoreMsg Question DiffAdd DiffChange DiffDelete DiffText SpellBad SpellCap SpellLocal SpellRare QuickFixLine Terminal Added Changed Removed Comment Constant String Character Number Boolean Float Identifier Function Statement Conditional Repeat Label Operator Keyword Exception PreProc Include Define Macro PreCondit Type StorageClass Structure Typedef Special SpecialChar Tag Delimiter SpecialComment Debug Underlined Ignore Error Todo', ' ')
let out = {'scheme': $CS, 'requested': $BG, 'background': &background, 'groups': {}}
for n in grp
  let id = hlID(n)
  if id == 0 | continue | endif
  let t = synIDtrans(id)
  let d = {'fg': synIDattr(t, 'fg#', 'gui'), 'bg': synIDattr(t, 'bg#', 'gui'), 'sp': synIDattr(t, 'sp#', 'gui')}
  for a in ['bold', 'italic', 'underline', 'undercurl', 'strikethrough', 'reverse']
    let d[a] = synIDattr(t, a, 'gui') == '1' ? 1 : 0
  endfor
  let out.groups[n] = d
endfor
if exists('g:terminal_ansi_colors') | let out.ansi = g:terminal_ansi_colors | endif
call writefile([json_encode(out)], $OUT)
qa!
