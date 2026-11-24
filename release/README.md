# Vim Colorschemes

The color schemes of Vim 9.2 as themes for VS Code and VSCodium. They are called **"Vim: Elflord"**, **"Vim: Habamax"** and so on (32 themes). Select one via *Preferences: Color Theme*.

The themes are generated automatically from Vim's own data: the colors come from Vim's color schemes, the words and structures from its syntax files. The goal is that code in VS Code looks like it does in gVim with the default settings (`defaults.vim`).

This extension replaces the former separate Vim theme extensions by r11s (Default, Desert, Elflord, Peachpuff). If you have them installed, you can remove them.

## Languages

The themes color these languages the way Vim does. Whether a file is colored at all depends on a grammar for the language being available in VS Code.

**Grammar built into VS Code** (no extra extension needed):
Go, Python, C, C++, C#, Java, JavaScript, TypeScript, Rust, Swift, Dart, Ruby, Perl, PHP, Lua, R, Shell, PowerShell, Batch, SQL, HTML, XML, CSS, SCSS, Less, JSON, YAML, INI, Markdown, Make, Dockerfile and Diff.

**Grammar provided by this extension:** Pascal.

**Needs a language extension:** Kotlin. VS Code has no grammar for Kotlin, so without a language extension Kotlin files are not colored at all, with any theme. The colors were tested with the grammar of the extension "Kotlin" by fwcd.

**Coming later:** Scala, Cobol, TOML and Vim script (VS Code has no grammar for them either; recommended extensions will follow), and other languages for which Vim has a syntax file.

Other languages, including Assembly, Ada, Fortran, Julia, Visual Basic, Objective-C and MATLAB, are not colored the way Vim does yet. MATLAB files (`.m`) are treated as Objective-C by VS Code.

## Recommended settings

VS Code draws some things in its own colors. To get closer to Vim, you can turn these off:

```json
"editor.bracketPairColorization.enabled": false,
"editor.semanticHighlighting.enabled": false
```

## Limitations

The themes follow Vim's syntax highlighting as closely as TextMate grammars allow. The result depends on the grammar VS Code uses for each language, so some constructs are colored differently than in Vim, and Vim's own quirks are not reproduced.

The colors were compared with gVim file by file for most of the languages above. For Make, Dockerfile, Diff, INI, HTML, XML, CSS, SCSS, Less, JSON, YAML, Markdown and Batch this comparison has not been done yet. They are generated the same way from Vim's syntax data, so they should be close, but differences are more likely there. If you find a difference that bothers you, please report it (see below).

## Feedback

Errors, wishes for more syntax and questions are welcome: **https://github.com/r11s/vim-colorschemes/issues**

Helpful: the theme, the language, a short code snippet and, if possible, a screenshot (gVim and VS Code side by side).

## License and origin

The extension is licensed under the Vim License (file `LICENSE`). Colors and word lists come from Vim 9.2 (`runtime/colors` and `runtime/syntax`). The colors of the user interface around the editor (tabs, side bar, status bar and so on) are derived from the VS Code default themes "Dark (Visual Studio)" and "Light (Visual Studio)" by Microsoft (MIT License, see `THIRD-PARTY-NOTICES.txt`). The grammars and the generator tool are newly written.

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
