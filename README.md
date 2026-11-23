# Vim Colorschemes

The color schemes of Vim 9.2 as themes for VS Code and VSCodium ("Vim: Elflord", "Vim: Habamax", …, 32 in total). They are generated automatically from Vim's data so that code looks like in gVim with `defaults.vim`.

This extension replaces the former separate Vim theme extensions (Default, Desert, Elflord, Peachpuff).

Details, supported languages, status and feedback: see [release/README.md](release/README.md). Changes: [release/CHANGELOG.md](release/CHANGELOG.md).

## Repository layout

- `release/` – the extension as it is published (package, grammars, themes, license).
- `tools/` – scripts that generate the grammars and themes from Vim's data. They are written for the author's working environment, paths may need adjusting.
- `data/` – data extracted from Vim 9.2 (colors, syntax word lists, scope-to-group pairs) that the tools work with.

## License

Vim License, see `release/LICENSE`.
