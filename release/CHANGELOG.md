# Changelog

## 1.0.3
- TypeScript: `readonly` after `private`, `public` or `protected` in constructor parameters now uses the Vim color for `readonly`.
- TypeScript: built-in names such as `console`, `Math`, `Date`, `Error` and their members (`console.log`, `Math.floor`, `toFixed`) now use the Vim colors.
- TypeScript: `function`, `interface` and the names in function declarations now use the Vim colors.
- TypeScript: variables are no longer colored like function arguments everywhere, only the editor text color is used.
- TypeScript: `abstract` now uses the Vim color for `abstract` (Special).
- TypeScript: variables inside `${...}` in template strings after `new` no longer use the argument color.
- Shell: `readonly`, `declare` and `typeset` now use the Vim color for statements.
- Shell: function definitions (`name() {` and the closing `}`) now use the Vim function color.
- Shell: command names inside `$( ... )` now use the Vim command substitution color.
- Shell: arithmetic `(( ... ))` and `for (( ... ))` now use the Vim colors, including comparison operators.

## 1.0.2
- README simplified and made more general; it no longer states accuracy figures.
- Fixed JavaScript colors: double-quoted strings, JSDoc comments, parts of regular expressions and `true`/`false` now use the Vim colors.
- Added the license notice for the user interface colors, which are derived from the VS Code default themes (MIT), as `THIRD-PARTY-NOTICES.txt`.

## 1.0.1
- Added an extension icon.
- README, changelog and description are now in English.
- Added links to the repository and the issue tracker (feedback, errors, wishes for more syntax).

## 1.0.0
- Replaces the former separate Vim theme extensions (Default, Desert, Elflord, Peachpuff).
- 32 color schemes of Vim 9.2 as themes "Vim: …".
- Languages: Go, Python, C, Java, JavaScript and 33 more (C++, C#, TypeScript, Rust, Ruby, Shell, CSS/SCSS/Less, HTML, XML, JSON, YAML, TOML, Markdown, SQL, Lua, Vim script, PowerShell, Batch, Perl, INI, Diff, Make, PHP, Dockerfile, Cobol, Swift, Dart, Kotlin, Scala, R).
- Pascal: own grammar, colored according to Vim (standard Pascal).
