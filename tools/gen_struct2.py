# python3 gen_struct2.py <inj_in> <inj_out>  -- Strukturfälle der weiteren Sprachen
import json, sys, shutil, os
src, out = sys.argv[1], sys.argv[2]
shutil.copytree(src, out, dirs_exist_ok=True)
index = json.load(open(f'{out}/index.json'))
GR = set(tuple(l.split('\t')) for l in open(f'{out}/groups_std.tsv').read().split('\n') if l)
def add(scope, name, selector, patterns, groups=()):
    json.dump({'scopeName': f'vim.injection.{name}', 'injectionSelector': selector, 'patterns': patterns}, open(f'{out}/{name}.json', 'w'), indent=1)
    index.setdefault(scope, []).append(f'vim.injection.{name}')
    for g in groups: GR.add(g)
def prepend(lang, pats):
    f = f'{out}/{lang}.json'; g = json.load(open(f)); g['patterns'] = pats + g['patterns']; json.dump(g, open(f, 'w'), indent=1)

# ---- TypeScript ----
add('source.ts', 'ts-doc', 'L:comment.block.documentation.ts source.embedded.ts',
    [{'match': r'(?:(?!```|\*/).)+', 'name': 'vim.Comment.typescriptDocComment'}], [('typescriptDocComment', 'Comment')])

# ---- SCSS: benutzerdefinierte Eigenschaften --x (TM: variable.scss wie $x) ----
add('source.css.scss', 'scss-customprop', 'L:source.css.scss -comment -string',
    [{'match': r'(?<![\w$@-])--[\w-]+', 'name': 'vim.Special.cssCustomProp'}], [('cssCustomProp', 'Special')])

add('source.css.scss', 'scss-var', 'L:source.css.scss -comment -string -vim.Function',
    [{'begin': r'\b(var)\s*(\()', 'end': r'\)', 'beginCaptures': {'1': {'name': 'vim.Function.cssFunctionName'}, '2': {'name': 'vim.Function.cssFunctionName'}},
      'endCaptures': {'0': {'name': 'vim.Function.cssFunctionName'}},
      'patterns': [{'include': '#v'}, {'match': r'(?<![\w$@-])--[\w-]+', 'name': 'vim.Special.cssCustomProp'}]}], [('cssFunctionName', 'Function')])
g = json.load(open(f'{out}/scss-var.json')); g['repository'] = {'v': {'begin': r'\b(var)\s*(\()', 'end': r'\)', 'beginCaptures': g['patterns'][0]['beginCaptures'], 'endCaptures': g['patterns'][0]['endCaptures'], 'patterns': [{'include': '#v'}, {'match': r'(?<![\w$@-])--[\w-]+', 'name': 'vim.Special.cssCustomProp'}]}}
g['patterns'][0]['patterns'][0] = {'include': '#v'}; json.dump(g, open(f'{out}/scss-var.json', 'w'), indent=1)

# ---- dosbatch: echo-Text, if-Operatoren, ::-Kommentar mitten in der Zeile ----
prepend('dosbatch', [
    {'match': r'(?i)\b(echo)(\s+(?:on|off)\s*$)', 'captures': {'1': {'name': 'vim.Function.dosbatchImplicit'}, '2': {'name': 'vim.Operator.dosbatchEchoOperator'}}},
    {'begin': r'(?i)\b(echo)\b', 'beginCaptures': {'1': {'name': 'vim.Function.dosbatchImplicit'}}, 'end': r'(?=[)>|])|$', 'contentName': 'vim.String.dosbatchString',
     'patterns': [{'match': r'%\h\w*%|!\h\w*!', 'name': 'vim.Identifier.dosbatchVariable'},
                  {'match': r'(?i)%(?:\d|\*)|%%[a-z]\b|%~[fdpnxsatz]+(?:(?:\$PATH:)?[a-z]|\d)\b', 'name': 'vim.Identifier.dosBatchArgument'},
                  {'match': r'\^[&|()<>^]|\$[a-hl-npqstv_$+]|%%', 'name': 'vim.SpecialChar.dosbatchSpecialChar'}]},
    {'match': r'(?i)\b(if)((?:\s+not)?\s+(?:exist|defined|errorlevel|cmdextversion))', 'captures': {'1': {'name': 'vim.Conditional.dosbatchConditional'}, '2': {'name': 'vim.Operator.dosbatchIfOperator'}}},
    {'match': r'\s*:\s*:.*$', 'name': 'vim.Comment.dosbatchColonComment'},
    {'match': r'^\s*:\s*\h\w*\b', 'name': 'vim.Label.dosbatchLabel'}])
for g in [('dosbatchEchoOperator', 'Operator'), ('dosbatchIfOperator', 'Operator'), ('dosbatchString', 'String'), ('dosbatchColonComment', 'Comment'), ('dosbatchVariable', 'Identifier'), ('dosBatchArgument', 'Identifier'), ('dosbatchSpecialChar', 'SpecialChar'), ('dosbatchLabel', 'Label')]: GR.add(g)

# ---- dosini: Zeilen wie Vim (Label/Wert/Zahl/Header/Kommentar) ----
NUM = r'(?:\d+|\d*\.\d+|\d+[eE][+-]?\d+)'
add('source.ini', 'ini-struct', 'L:source.ini',
    [{'match': r'^[#;].*$', 'name': 'vim.Comment.dosiniComment'},
     {'match': r'^\s*\[[^\]]*\]', 'name': 'vim.Special.dosiniHeader'},
     {'match': r'^(.*?)(\s*=)(\s*' + NUM + r'\s*)$', 'captures': {'1': {'name': 'vim.Type.dosiniLabel'}, '3': {'name': 'vim.Number.dosiniNumber'}}},
     {'match': r'^(.*?)(\s*=)(.*)$', 'captures': {'1': {'name': 'vim.Type.dosiniLabel'}, '3': {'name': 'vim.String.dosiniValue'}}},
     {'match': r'^.+$', 'name': 'vim.Normal'}],
    [('dosiniComment', 'Comment'), ('dosiniHeader', 'Special'), ('dosiniLabel', 'Type'), ('dosiniNumber', 'Number'), ('dosiniValue', 'String')])

json.dump(index, open(f'{out}/index.json', 'w'))
open(f'{out}/groups_std.tsv', 'w').write('\n'.join(f'{g}\t{s}' for g, s in sorted(GR)) + '\n')
