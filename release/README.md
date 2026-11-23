# Vim Colorschemes

The color schemes of Vim 9.2 as themes for VS Code and VSCodium. They are called **"Vim: Elflord"**, **"Vim: Habamax"** and so on (32 in total, select them via *Color Theme* in the settings).

The themes are generated automatically from Vim's data: colors from the schemes, words and structures from Vim's syntax files. The goal is that code in VS Code looks the same as in gVim with the default setting `defaults.vim`.

## Replaces the former Vim extensions

This extension replaces the former separate Vim theme extensions by r11s (Default, Desert, Elflord, Peachpuff). All of these themes are included here, and the colors match Vim more closely. If you have the old extensions installed, you can remove them.

## Status

Feedback and wishes are welcome (see below).

- Measured against Vim, the colors match by more than 99 % for Go, Python, C, Java and JavaScript (real, previously unseen code), and by about 90 % on average for the other languages.
- Like the other languages, Pascal follows Vim's syntax for standard Pascal. Comments are `{ … }` and `(* … *)`. `//` is not part of standard Pascal (Vim only knows it with the setting `pascal_delphi`), so it is not a comment here either. A small Pascal grammar of its own is included for this.
- Known deviations from Vim that are intentionally not reproduced: Vim bugs, such as the wrong coloring of `echo:Text` in batch files or the string errors in Makefile recipes.

## Languages

The themes color these languages like Vim does:

Go, Python, C, C++, C#, Java, JavaScript, TypeScript, Rust, Swift, Dart, Kotlin, Scala, Ruby, Perl, PHP, Lua, R, Shell, PowerShell, Batch, SQL, HTML, XML, CSS, SCSS, Less, JSON, YAML, TOML, INI, Markdown, Make, Dockerfile, Diff, Cobol and Vim script.

This requires that VS Code has a grammar for the language. For **Kotlin, Scala, Cobol, TOML and Vim script** VS Code does not ship one, so a suitable language extension must be installed. Otherwise the file is not colored.

**Pascal** is provided by this extension itself (file extensions `.pas .pp .p .inc .dpr .dpk .lpr .lpk`), see "Status".

## Recommendation

It is best to turn off `editor.bracketPairColorization`, because VS Code otherwise draws brackets in its own colors:

```json
"editor.bracketPairColorization.enabled": false
```

Likewise `"editor.semanticHighlighting.enabled": false` fits Vim better.

## Feedback, wishes and questions

If something is not right, please open an issue here: **https://github.com/r11s/vim-colorschemes/issues**

Welcome are:
- **Errors**: places where VS Code looks different from gVim.
- **Wishes for more syntax**: languages or file formats that are still missing.
- **Questions** about the extension.

Helpful: the theme, the language, a short code snippet and a screenshot (gVim and VS Code side by side).

## License and origin

The extension is licensed under the Vim License (file `LICENSE`). Colors and word lists come from Vim 9.2 (`runtime/colors` and `runtime/syntax`). The grammars and the generator tool are newly written. The Pascal grammar is also original.

Author and license of the color schemes, as given in the header lines of the Vim files:

| Scheme | Author | License according to file |
| --- | --- | --- |
| blue | Steven Vertigan | same as Vim |
| catppuccin | The Catppuccin Community (maintained by Mao-Yining) | not stated in the file |
| darkblue | Bohdan Vlasyuk | same as Vim |
| default | The Vim Project (formerly Bram Moolenaar) | not stated in the file |
| delek | David Schweikert | same as Vim |
| desert | Hans Fugal | same as Vim |
| elflord | Ron Aaron | same as Vim |
| evening | Bram Moolenaar (maintained by Steven Vertigan) | same as Vim |
| habamax | Maxim Kim | same as Vim |
| industry | Shian Lee | same as Vim |
| koehler | Ron Aaron | same as Vim |
| lunaperche | Maxim Kim | not stated in the file |
| morning | Bram Moolenaar | same as Vim |
| murphy | Ron Aaron | same as Vim |
| pablo | Ron Aaron | same as Vim |
| peachpuff | David Nečas (Yeti) | same as Vim |
| quiet | Maxence Weynans | Vim License |
| retrobox | Maxim Kim, ported from gruvbox8 (Lifepillar); gruvbox by morhetz | not stated in the file |
| ron | Ron Aaron | same as Vim |
| shine | Yasuhiro Matsumoto | same as Vim |
| slate | Ralph Amissah | same as Vim |
| sorbet | Maxence Weynans | Vim License |
| torte | Thorsten Maerz | same as Vim |
| unokai | k-37, similar to Monokai by Wimer Hazenberg | not stated in the file |
| wildcharm | Maxim Kim | same as Vim |
| zaibatsu | Romain Lafourcade | same as Vim |
| zellner | Ron Aaron | same as Vim |

The information is taken from the header lines of the Vim files. Where it says "not stated in the file", the header does not name a license.
