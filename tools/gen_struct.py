# python3 gen_struct.py <inj_in> <inj_out>
# Struktur-Injektionen "wie Vim": Todo, C-Regionen, Zeichenliterale, Labels, ...
import csv, json, sys, os, collections, shutil
VD = os.environ.get('VD', '/tmp/vd')       # Arbeitsverzeichnis (Zwischenstände, Beispielprojekte)
src, out = sys.argv[1], sys.argv[2]
shutil.copytree(src, out, dirs_exist_ok=True)
W = VD + '/words/gen/'
L = {'go': ('source.go', 'go'), 'python': ('source.python', 'py'), 'c': ('source.c', 'c'), 'java': ('source.java', 'java'), 'javascript': ('source.js', 'js')}
index = json.load(open(f'{out}/index.json'))

GROUPS = set()
def word_patterns(lang):
    scope, ext = L[lang]
    lines = open(f'{W}{lang}.{ext}', encoding='utf-8').read().split('\n')
    by = collections.defaultdict(set)
    for r in csv.reader(open(f'{W}{lang}.el.std.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
        if len(r) < 5 or r[3] == '#END': continue
        word = lines[int(r[0]) - 1].strip(); std = r[4]; vg = r[3]
        if std in ('None', '', 'Normal') or std.startswith(lang) or not word.isidentifier(): continue
        by[(std, vg)].add(word)
    pats = []
    for (std, vg), ws in sorted(by.items()):
        ws = sorted(ws, key=lambda w: (-len(w), w))
        pats.append({'match': r'\b(?:' + '|'.join(ws) + r')\b', 'name': f'vim.{std}.{vg}'})
        GROUPS.add((vg, std))
    return pats

for _lang, (_scope, _ext) in L.items():
    json.dump({'scopeName': f'vim.injection.{_lang}', 'injectionSelector': f'L:{_scope} -comment -string', 'patterns': word_patterns(_lang)},
              open(f'{out}/{_lang}.json', 'w'), indent=1)

def prepend(lang, pats):
    f = f'{out}/{lang}.json'
    g = json.load(open(f))
    g['patterns'] = pats + g['patterns']
    json.dump(g, open(f, 'w'), indent=1)

def add(lang, name, selector, patterns):
    g = {'scopeName': f'vim.injection.{name}', 'injectionSelector': selector, 'patterns': patterns}
    json.dump(g, open(f'{out}/{name}.json', 'w'), indent=1)
    index[L[lang][0]].append(g['scopeName'])

TODO = {'go': 'TODO|FIXME|XXX|BUG|NOTE', 'python': 'FIXME|NOTE|NOTES|TODO|XXX', 'c': 'TODO|FIXME|XXX',
        'java': 'TODO|FIXME|XXX', 'javascript': 'TODO|FIXME|XXX|TBD'}
for lang, words in TODO.items():
    TG = {'go': 'goTodo', 'python': 'pythonTodo', 'c': 'cTodo', 'java': 'javaTodo', 'javascript': 'javaScriptCommentTodo'}
    GROUPS.add((TG[lang], 'Todo'))
    add(lang, f'{lang}-todo', f'L:{L[lang][0]} comment', [{'match': r'\b(?:' + words + r')\b', 'name': 'vim.Todo.' + TG[lang]}])

# ---- C ----
FILL = [{'match': r'[A-Za-z_]\w*|[^\s\w"\'/]|/(?![/*])', 'name': 'vim.%s'}]
def fill(std, vg=None):
    if vg: GROUPS.add((vg, std))
    return [dict(FILL[0], name=f'vim.{std}' + (f'.{vg}' if vg else ''))]
add('c', 'c-define', 'L:meta.preprocessor.macro.c -comment -string', word_patterns('c') + fill('Macro', 'cDefine'))
add('c', 'c-precond', 'L:meta.preprocessor.c -comment -string', fill('PreCondit', 'cPreCondit'))
add('c', 'c-char', 'L:source.c -comment -string',
    [{'match': r"L?'\\(?:['\"?\\abefnrtv]|[0-7]{1,3}|x[0-9a-fA-F]{1,2})'", 'name': 'vim.SpecialChar.cSpecialCharacter'}])
add('c', 'c-label', 'L:source.c -comment -string',
    [{'match': r'(?:^\s*|;\s*)((?!default\b)[A-Za-z_]\w*)(?=\s*:(?!:)(?!\s*[1-9]))', 'captures': {'1': {'name': 'vim.Label.cUserLabel'}}}])


# ---- C: Strings/Zeichen/Zahlen in Kommentaren (defaults.vim setzt c_comment_strings=1) ----
CSPEC = {'match': r'\\(?:x[0-9a-fA-F]+|[0-7]{1,3}|.|$)', 'name': 'vim.Special.cSpecial'}
CSKIP = {'match': r'^\s*\*(?:$|\s+)', 'name': 'vim.Comment.cCommentSkip'}
NUM = (r"(?<![\w.])(?:0[xX][0-9a-fA-F]+(?:'[0-9a-fA-F]+)*(?:[uU]?[lL]{0,2}|[lL]{1,2}[uU])"
       r"|0[bB][01]+(?:'[01]+)*(?:[uU]?[lL]{0,2}|[lL]{1,2}[uU])"
       r"|\d+(?:'\d+)*(?:[uU]?[lL]{0,2}|[lL]{1,2}[uU])"
       r")(?![\w.])")
FLT = (r"(?<![\w.])(?:\d+[fF]|\d+\.\d*(?:[eE][-+]?\d+)?[fFlL]?|\d+[eE][-+]?\d+[fFlL]?)(?![\w.])"
       r"|(?<![\w])\.\d+(?:[eE][-+]?\d+)?[fFlL]?(?![\w.])")
common = [{'match': r"L?'[^\\']'|L'[^']*'", 'name': 'vim.Character.cCharacter'},
          {'match': NUM, 'name': 'vim.Number.cNumber'}, {'match': FLT, 'name': 'vim.Float.cFloat'}]
GROUPS.update([('cCommentString', 'String'), ('cComment2String', 'String'), ('cSpecial', 'Special'), ('cCommentSkip', 'Comment'),
               ('cCharacter', 'Character'), ('cNumber', 'Number'), ('cFloat', 'Float')])
add('c', 'c-comment-block', 'L:comment.block.c -vim.String', [
    {'begin': r'(?<!\\)L?"', 'end': r'"|(?=\*/)', 'name': 'vim.String.cCommentString', 'patterns': [CSKIP, CSPEC]}] + common)
add('c', 'c-comment-line', 'L:comment.line.double-slash.c -vim.String', [
    {'begin': r'(?<!\\)L?"', 'end': r'"|$', 'name': 'vim.String.cComment2String', 'patterns': [CSPEC]}] + common)

# ---- Java ----
INL = r'\{@(?:code|link|linkplain|literal|value|docRoot|inheritDoc|index|systemProperty|snippet)\b[^}]*\}'
title = {'begin': r'(?<=/\*\*)', 'end': r'\.(?=\s|$)|(?=\*/)|(?=^\s*\*+\s*@)', 'name': 'vim.SpecialComment',
         'patterns': [{'match': r'^\s*\*+(?!/)', 'name': 'vim.Comment'}, {'match': INL, 'name': 'vim.Special'}]}
add('java', 'java-doc', 'L:comment.block.javadoc.java -vim.SpecialComment', [
    title,
    {'match': INL, 'name': 'vim.Special'},
    {'match': r'(@(?:param|exception|throws|since))(\s+)(\S+)', 'captures': {'1': {'name': 'vim.Special'}, '3': {'name': 'vim.Function'}}},
    {'match': r'(@see)(\s+)((?:[\w/.$])*(?:#\w+(?:\([^)]*\))?)?)', 'captures': {'1': {'name': 'vim.Special'}, '3': {'name': 'vim.Function'}}},
    {'match': r'@(?:author|deprecated|hidden|return|serial|serialData|serialField|version)\b', 'name': 'vim.Special'},
])
add('java', 'java-misc', 'L:source.java -comment -string', [
    {'match': r'^\s*(?!default\b)([A-Za-z_$][\w$]*)\s*(?=:(?!:))', 'captures': {'1': {'name': 'vim.Label.javaUserLabel'}}},
    {'match': r'(?:(?<=\bbreak[ \t])|(?<=\bcontinue[ \t]))[A-Za-z_$][\w$]*', 'name': 'vim.Label.javaUserLabelRef'},
])
prepend('java', [{'match': r'\bimport\b(?:\s+static\b)?', 'name': 'vim.Include.javaExternal'}])

def dot_patterns(lang):
    out = []
    for p in word_patterns(lang):
        out.append({'match': r'(?<!\d)\.(\s*)' + p['match'].replace(r'\b(?:', r'\b(?:', 1), 'captures': {}, '_n': p['name']})
    res = []
    for p in out:
        m = p['match']
        # Gruppe 2 = das Wort
        m = m.replace(r'\.(\s*)\b(?:', r'\.(\s*)(\b(?:', 1)
        assert m.endswith(r')\b')
        m = m + ')'
        res.append({'match': m, 'captures': {'2': {'name': p['_n']}}})
    return res
for lang in ('javascript', 'java'):
    prepend(lang, dot_patterns(lang))
prepend('java', [{'match': r'\.(\s*)(class)\b', 'captures': {'2': {'name': 'vim.Typedef.javaTypedef'}}}])

# ---- JavaScript ----
add('javascript', 'js-embed', 'L:meta.template.expression.js', [p for p in word_patterns('javascript') if p['name'].startswith(('vim.Boolean', 'vim.Identifier'))] +
    [{'match': r'[A-Za-z_$][\w$]*|\d[\w.]*|[^\s\w$\'"`{}]', 'name': 'vim.Special'}])
add('javascript', 'js-misc', 'L:source.js -comment -string', [
    {'match': r'\b(?:0[xX][\da-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|\d[\d_]*)n\b', 'name': 'vim.Normal'}])
add('javascript', 'js-esc', 'L:string.quoted.single.js, L:string.quoted.double.js, L:string.template.js',
    [{'match': r'\\(?:\d\d\d|.)', 'name': 'vim.Special'}])

# ---- Python ----
py_first = [
    {'match': r'\b(async)(\s+)(def)(\s+)([A-Za-z_]\w*)', 'captures': {'1': {'name': 'vim.Statement.pythonStatement'}, '3': {'name': 'vim.Statement.pythonStatement'}, '5': {'name': 'vim.Function.pythonFunction'}}},
    {'match': r'\b(def)(\s+)([A-Za-z_]\w*)', 'captures': {'1': {'name': 'vim.Statement.pythonStatement'}, '3': {'name': 'vim.Function.pythonFunction'}}},
    {'match': r'\b(class)(\s+)([A-Za-z_]\w*)', 'captures': {'1': {'name': 'vim.Statement.pythonStatement'}, '3': {'name': 'vim.Structure.pythonClass'}}},
    {'match': r'\b(type)(\s+)([A-Za-z_]\w*)(?=\s*(?:\[|=))', 'captures': {'1': {'name': 'vim.Statement.pythonStatement'}, '3': {'name': 'vim.Type.pythonType'}}},
]
prepend('python', py_first)
doctest = {'begin': r'^\s*>>>\s', 'end': r'^\s*$|^(?=\s*(?:"""|\'\'\'))|(?=""")|(?=\'\'\')', 'name': 'vim.Special',
           'patterns': [{'match': r'^\s*(?!>>>\s|\.\.\.\s|"""|\'\'\')\S.*$', 'name': 'vim.Define'}] + word_patterns('python') + [{'match': r'[A-Za-z_]\w*|[^\s\w"\']', 'name': 'vim.Special'}, {'include': 'source.python'}]}
add('python', 'py-doctest', 'L:string.quoted.docstring.multi.python -vim.Special, L:string.quoted.multi.python -vim.Special', [doctest])
add('python', 'py-regexp', 'L:string.regexp.quoted.single.python, L:string.regexp.quoted.multi.python', [
    {'match': r'(?:\\.|[^\s\\\'"])+', 'name': 'vim.String'}])
add('python', 'py-fstr', 'L:meta.fstring.python', [{'match': r'\{\{|\}\}', 'name': 'vim.String'}])

GROUPS.update([('cSpecialCharacter','SpecialChar'),('cUserLabel','Label'),('javaUserLabel','Label'),('javaUserLabelRef','Label'),('javaExternal','Include'),('javaTypedef','Typedef'),('pythonStatement','Statement'),('pythonFunction','Function'),('pythonClass','Structure'),('pythonType','Type')])
json.dump(index, open(f'{out}/index.json', 'w'))
open(f'{out}/groups_std.tsv', 'w').write('\n'.join(f'{g}\t{s}' for g, s in sorted(GROUPS)) + '\n')
