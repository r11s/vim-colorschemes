# Vim Colorschemes

The color schemes of Vim 9.2 as themes for VS Code and VSCodium ("Vim: Elflord", "Vim: Habamax", …, 32 in total). They are generated automatically from Vim's data so that code looks like in gVim with `defaults.vim`.

This extension replaces the former separate Vim theme extensions (Default, Desert, Elflord, Peachpuff).

Details, supported languages, status and feedback: see [release/README.md](release/README.md). Changes: [release/CHANGELOG.md](release/CHANGELOG.md).

## Repository layout

- `release/` – the extension as it is published (package, grammars, themes, license).
- `tools/` – scripts that generate the grammars and themes from Vim's data. They were written for the author's working environment; the paths can be set with environment variables: `VD` (working directory, default `/tmp/vd`), `TM` (default `/tmp/tm`), `VIM` (Vim 9.2 binary, default `/tmp/vim92/bin/vim`) and `RT92` (Vim's runtime files, default: `rt92/` in this repository, otherwise `$VD/rt92`). `tools/spec.json` and `tools/more_train.py` still name the example projects under `/tmp/vd/lang/repos/` that were used for training.
- `rt92/` – optional local copy of Vim 9.2's runtime files (`colors`, `syntax`, …); not tracked, see `.gitignore`.
- `data/` – data extracted from Vim 9.2 (colors, syntax word lists, scope-to-group pairs) that the tools work with.

## License

Vim License, see `release/LICENSE`.
