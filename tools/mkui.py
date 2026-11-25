#!/usr/bin/env python3
"""mkui.py -- erzeugt die Oberflächenfarben (`colors`) eines Themes aus dem Vim-Farbschema.

Aufruf:  python3 tools/mkui.py <theme.json> [<theme.json> ...]
Liest je Theme die Vim-Gruppen aus data/colors/<schema>.<dark|light>.json und ersetzt im Theme
alle `colors`, ausser den Editor-Schlüsseln, die schon aus Vim stammen (EDITOR_KEYS).

Rezept (ohne Vorlage anderer Themes, nur aus Normal und wenigen Vim-Gruppen):
  Flächen    Editor-Hintergrund, dazu Stufen Richtung Editor-Vordergrund (Seitenleiste/Panel, Tab-Leiste,
             Titel-/Aktivitätsleiste, Hover, Rahmen). Die Stufen nehmen die Tönung des Themes an.
  Akzent     Hintergrund von StatusLine (sonst Title, Statement, Constant), muss sich vom Editor abheben.
  Statuszeile  StatusLine; Listenauswahl, Menüs, Widgets  PmenuSel/Pmenu; Terminal  Vims ANSI-Farben;
  Diff       DiffAdd/DiffChange/DiffDelete; Fehler/Warnung  ErrorMsg/WarningMsg.
Jeder Text bekommt mindestens Kontrast 4.5 (Nebentext 3.5) gegen seinen Hintergrund."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data', 'colors')

EDITOR_KEYS = ('editor.background', 'editor.foreground', 'editor.lineHighlightBackground', 'editor.selectionBackground',
               'editorBracketMatch.background', 'editor.findMatchBackground', 'editor.findMatchHighlightBackground',
               'editor.foldBackground', 'editorCursor.foreground', 'editorLineNumber.foreground',
               'editorLineNumber.activeForeground', 'editorWhitespace.foreground', 'editorRuler.foreground',
               'editorBracketMatch.border')

def rgb(c):
    c = c.lstrip('#')
    if len(c) in (3, 4): c = ''.join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
def tohex(t): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in t)
def blend(a, b, t): return tohex(tuple(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))
def alpha(c, a): return c[:7] + '%02x' % round(a * 255)
def lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(c[:7])
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def contrast(a, b):
    la, lb = lum(a), lum(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)

def build(theme):
    """theme: dict eines Themes -> neues colors-Dict."""
    old = theme['colors']
    NBG, NFG = old['editor.background'], old['editor.foreground']
    dark = theme['type'] == 'dark'
    D = json.load(open(os.path.join(DATA, theme['_data'])))
    G = D['groups']
    def eff(g):
        x = G.get(g)
        if not x: return (None, None)
        fg, bg = x['fg'] or None, x['bg'] or None
        if x['reverse']: fg, bg = (bg or NBG), (fg or NFG)
        return (fg, bg)
    fgo = lambda g: eff(g)[0]
    bgo = lambda g: eff(g)[1]
    far = '#ffffff' if dark else '#000000'          # Ziel, um Text lesbarer zu machen

    def ensure(fg, bg, minc=4.5):
        """fg so weit Richtung Schwarz/Weiss schieben, bis der Kontrast zu bg reicht."""
        if contrast(fg, bg) >= minc: return fg
        tgt = '#ffffff' if contrast('#ffffff', bg) >= contrast('#000000', bg) else '#000000'
        for i in range(1, 21):
            c = blend(fg, tgt, i / 20)
            if contrast(c, bg) >= minc: return c
        return tgt
    def pick(bg, *cands, minc=4.5):                  # beste Textfarbe auf bg: erste Kandidatin mit Kontrast, sonst angepasst
        for c in cands:
            if c and contrast(c, bg) >= minc: return c
        return ensure(cands[0] or NFG, bg, minc)
    mx, mn = max(rgb(NBG)), min(rgb(NBG))
    chromatic = mx > 0 and (mx - mn) / mx > 0.5      # kräftig getönter Hintergrund (z. B. Blue): Stufen bleiben im Farbton
    TGT = far if chromatic else NFG
    def surf(t, mind):
        """Stufe zwischen Editor-Hintergrund (t=0) und Ziel (t=1); mindestens mind Helligkeitsunterschied."""
        while True:
            c = blend(NBG, TGT, t)
            if abs(lum(c) - lum(NBG)) >= mind or t >= 0.45: return c
            t += 0.01
    def dim(bg, minc=4.5): return ensure(blend(NFG, bg, 0.42), bg, minc)
    def on(bg):                                      # lesbare Schrift auf bg
        best = '#ffffff' if contrast('#ffffff', bg) >= contrast('#000000', bg) else '#000000'
        return pick(bg, NFG, far, best)

    side = surf(0.05, 0.008)
    tabbar = surf(0.09, 0.016)
    chrome = surf(0.12, 0.022)
    hover = surf(0.15, 0.03)
    inact = surf(0.21, 0.045)
    border = surf(0.24, 0.06)
    guide = surf(0.14, 0.03)
    guide_act = surf(0.34, 0.12)
    field = surf(0.08, 0.014)

    # Akzent
    accent = None
    for cand in (bgo('StatusLine'), fgo('Title'), fgo('Statement'), fgo('Constant'), fgo('Identifier')):
        if cand and contrast(cand, NBG) >= 3: accent = cand; break
    if not accent: accent = NFG
    accent_fg = on(accent)
    accent_text = ensure(accent, NBG, 3.0)           # Akzent als Schrift/Linie auf Editor- bzw. Flächenfarbe

    # Statuszeile (Vims StatusLine)
    # Statusleiste wie Titel-/Menüleiste (ruhige Fläche), nicht die oft grelle StatusLine-Farbe
    sl_bg = chrome
    sl_fg = on(chrome)
    dbg = bgo('ErrorMsg') or '#cc0000'
    dbg_fg = on(dbg)
    rem_bg = bgo('PmenuSel') or accent
    rem_fg = on(rem_bg)

    # Popup-Menü (Menüs, Widgets, Vorschläge)
    pm_bg, pm_fg = bgo('Pmenu'), fgo('Pmenu')
    if not pm_bg or abs(lum(pm_bg) - lum(NBG)) < 0.01: pm_bg = surf(0.14, 0.03)
    # Grosse Flächen (Menüs, Quick-Pick, Widgets): sehr kräftige Pmenu-Farben (z. B. Default #ff8bff) nur als Tönung übernehmen
    _mx, _mn = max(rgb(pm_bg)), min(rgb(pm_bg))
    if _mx > 100 and (_mx - _mn) / _mx > 0.3: pm_bg = blend(pm_bg, NBG, 0.75)
    pm_fg = pick(pm_bg, pm_fg, NFG, far)
    ps_bg, ps_fg = bgo('PmenuSel'), fgo('PmenuSel')
    if not ps_bg or contrast(ps_bg, pm_bg) < 1.4: ps_bg = blend(NBG, accent, 0.45)
    ps_fg = pick(ps_bg, ps_fg, NFG, far)
    # Listenauswahl in Seitenleiste: wie PmenuSel, aber nur gedämpft, wenn sie sehr hell ist
    lsel_bg = lsel_fg = None
    for t in (0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15):
        b = blend(side, ps_bg, t)
        if contrast(NFG, b) >= 4.5: lsel_bg, lsel_fg = b, NFG; break
    if not lsel_bg: lsel_bg = surf(0.28, 0.06); lsel_fg = on(lsel_bg)
    # Menüs, Quick-Pick, Find-/Hover-Widgets: ruhige Fläche (in gvim sind Menüs neutral); Pmenu gilt nur für die Vorschlagsliste
    wd_bg = surf(0.08, 0.014)
    wd_fg = pick(wd_bg, NFG, far)

    # Fehler, Warnung, Info
    def colorful(c): return c and (max(rgb(c)) - min(rgb(c))) > 90
    err = None
    for cand in (bgo('ErrorMsg'), fgo('ErrorMsg'), bgo('Error'), fgo('Error'), '#ff0000'):
        if colorful(cand) and contrast(cand, NBG) >= 3: err = cand; break
    err = err or ensure('#ff0000', NBG, 3.0)
    warn = None
    for cand in (fgo('WarningMsg'), bgo('WarningMsg'), bgo('Todo'), '#ffa500'):
        if colorful(cand) and contrast(cand, NBG) >= 3: warn = cand; break
    warn = warn or ensure('#ffa500', NBG, 3.0)
    info = ensure(fgo('Directory') or accent, NBG, 3.0)

    dimside, dimtab, dimchr = dim(side), dim(tabbar), dim(chrome)

    c = {k: old[k] for k in EDITOR_KEYS if k in old}
    c['editorError.foreground'] = err
    c['editorWarning.foreground'] = warn
    c['editorInfo.foreground'] = info
    # Allgemein
    c.update({
        'foreground': NFG, 'descriptionForeground': dim(NBG), 'disabledForeground': dim(NBG, 3.0),
        'errorForeground': err, 'focusBorder': accent_text, 'widget.border': border, 'widget.shadow': alpha(far if not dark else '#000000', 0.35),
        'selection.background': alpha(c.get('editor.selectionBackground', accent), 0.9),
        'icon.foreground': NFG,
        'textLink.foreground': accent_text, 'textLink.activeForeground': ensure(blend(accent, far, 0.25), NBG, 3.0),
        'textCodeBlock.background': side, 'textBlockQuote.background': side, 'textBlockQuote.border': border,
        'textPreformat.foreground': NFG, 'textSeparator.foreground': border,
        'scrollbar.shadow': '#00000000',
        'scrollbarSlider.background': alpha(NFG, 0.22), 'scrollbarSlider.hoverBackground': alpha(NFG, 0.36),
        'scrollbarSlider.activeBackground': alpha(NFG, 0.5),
        'progressBar.background': accent_text,
        'badge.background': accent, 'badge.foreground': accent_fg,
        'sash.hoverBorder': accent_text,
    })
    # Editor (Ergänzungen)
    c.update({
        'editorIndentGuide.background1': guide, 'editorIndentGuide.activeBackground1': guide_act,
        'editorGutter.background': NBG,
        'editorGutter.addedBackground': bgo('DiffAdd') or fgo('DiffAdd') or accent,
        'editorGutter.modifiedBackground': bgo('DiffChange') or fgo('DiffChange') or accent,
        'editorGutter.deletedBackground': bgo('DiffDelete') or fgo('DiffDelete') or err,
        'editorLink.activeForeground': accent_text,
        'editor.rangeHighlightBackground': alpha(NFG, 0.08),
        'editor.inactiveSelectionBackground': alpha(c.get('editor.selectionBackground', accent), 0.5),
        'editorGroup.border': border, 'editorGroup.dropBackground': alpha(accent, 0.25),
        'editorGroupHeader.tabsBackground': tabbar, 'editorGroupHeader.noTabsBackground': NBG,
        'editorGroupHeader.tabsBorder': border,
        'editorWidget.background': wd_bg, 'editorWidget.foreground': wd_fg, 'editorWidget.border': border,
        'editorHoverWidget.background': wd_bg, 'editorHoverWidget.foreground': wd_fg, 'editorHoverWidget.border': border,
        'editorHoverWidget.statusBarBackground': surf(0.2, 0.04),
        'editorSuggestWidget.background': pm_bg, 'editorSuggestWidget.foreground': pm_fg, 'editorSuggestWidget.border': border,
        'editorSuggestWidget.selectedBackground': ps_bg, 'editorSuggestWidget.selectedForeground': ps_fg,
        'editorSuggestWidget.highlightForeground': ensure(accent, pm_bg, 3.0),
        'editorOverviewRuler.border': '#00000000', 'editorOverviewRuler.background': NBG,
        'minimap.background': NBG, 'minimapSlider.background': alpha(NFG, 0.16),
        'minimapSlider.hoverBackground': alpha(NFG, 0.26), 'minimapSlider.activeBackground': alpha(NFG, 0.36),
        'peekView.border': accent_text, 'peekViewEditor.background': side, 'peekViewEditorGutter.background': side,
        'peekViewResult.background': tabbar, 'peekViewResult.fileForeground': NFG, 'peekViewResult.lineForeground': dim(tabbar),
        'peekViewResult.selectionBackground': ps_bg, 'peekViewResult.selectionForeground': ps_fg,
        'peekViewTitle.background': chrome, 'peekViewTitleLabel.foreground': NFG, 'peekViewTitleDescription.foreground': dim(chrome),
        'peekViewEditor.matchHighlightBackground': alpha(accent, 0.4), 'peekViewResult.matchHighlightBackground': alpha(accent, 0.4),
        'diffEditor.insertedTextBackground': alpha(bgo('DiffAdd') or accent, 0.35),
        'diffEditor.removedTextBackground': alpha(bgo('DiffDelete') or err, 0.35),
        'diffEditor.insertedLineBackground': alpha(bgo('DiffAdd') or accent, 0.2),
        'diffEditor.removedLineBackground': alpha(bgo('DiffDelete') or err, 0.2),
        'diffEditor.diagonalFill': alpha(bgo('DiffChange') or NFG, 0.35),
    })
    # Tabs
    c.update({
        'tab.activeBackground': NBG, 'tab.activeForeground': NFG, 'tab.activeBorderTop': accent_text,
        'tab.inactiveBackground': tabbar, 'tab.inactiveForeground': dimtab,
        'tab.unfocusedActiveBackground': NBG, 'tab.unfocusedActiveForeground': dim(NBG),
        'tab.unfocusedInactiveBackground': tabbar, 'tab.unfocusedInactiveForeground': dim(tabbar, 3.5),
        'tab.border': border, 'tab.hoverBackground': hover, 'tab.hoverForeground': on(hover),
        'tab.unfocusedHoverBackground': hover, 'tab.lastPinnedBorder': border,
        'breadcrumb.foreground': dim(NBG), 'breadcrumb.focusForeground': NFG, 'breadcrumb.activeSelectionForeground': NFG,
        'breadcrumb.background': NBG, 'breadcrumbPicker.background': wd_bg,
    })
    # Seitenleiste, Aktivitätsleiste, Titelleiste, Panel
    c.update({
        'sideBar.background': side, 'sideBar.foreground': on(side), 'sideBar.border': border,
        'sideBarTitle.foreground': on(side),
        'sideBarSectionHeader.background': tabbar, 'sideBarSectionHeader.foreground': on(tabbar), 'sideBarSectionHeader.border': border,
        'activityBar.background': chrome, 'activityBar.foreground': on(chrome), 'activityBar.inactiveForeground': dimchr,
        'activityBar.border': border, 'activityBar.activeBorder': accent_text,
        'activityBarBadge.background': accent, 'activityBarBadge.foreground': accent_fg,
        'titleBar.activeBackground': chrome, 'titleBar.activeForeground': on(chrome),
        'titleBar.inactiveBackground': tabbar, 'titleBar.inactiveForeground': dimtab, 'titleBar.border': border,
        'panel.background': side, 'panel.border': border, 'panelTitle.activeForeground': on(side),
        'panelTitle.inactiveForeground': dimside, 'panelTitle.activeBorder': accent_text,
        'panelSectionHeader.background': tabbar, 'panelSectionHeader.foreground': on(tabbar),
        'commandCenter.background': tabbar, 'commandCenter.foreground': on(tabbar), 'commandCenter.border': border,
        'commandCenter.activeBackground': hover, 'commandCenter.activeForeground': on(hover),
    })
    # Statuszeile
    c.update({
        'statusBar.background': sl_bg, 'statusBar.foreground': sl_fg, 'statusBar.border': border,
        'statusBar.noFolderBackground': sl_bg, 'statusBar.noFolderForeground': sl_fg,
        'statusBar.debuggingBackground': dbg, 'statusBar.debuggingForeground': dbg_fg,
        'statusBarItem.hoverBackground': alpha(sl_fg, 0.18), 'statusBarItem.hoverForeground': sl_fg,
        'statusBarItem.remoteBackground': rem_bg, 'statusBarItem.remoteForeground': rem_fg,
        'statusBarItem.prominentBackground': alpha(sl_fg, 0.25), 'statusBarItem.prominentForeground': sl_fg,
        'statusBarItem.errorBackground': dbg, 'statusBarItem.errorForeground': dbg_fg,
        'statusBarItem.warningBackground': warn, 'statusBarItem.warningForeground': on(warn),
    })
    # Listen, Bäume, Menüs, Eingaben, Knöpfe
    c.update({
        'list.activeSelectionBackground': lsel_bg, 'list.activeSelectionForeground': lsel_fg,
        'list.focusBackground': lsel_bg, 'list.focusForeground': lsel_fg, 'list.focusOutline': accent_text,
        'list.inactiveSelectionBackground': inact, 'list.inactiveSelectionForeground': on(inact),
        'list.inactiveFocusBackground': inact,
        'list.hoverBackground': hover, 'list.hoverForeground': on(hover),
        'list.highlightForeground': ensure(accent, side, 3.0), 'list.dropBackground': alpha(accent, 0.25),
        'list.errorForeground': err, 'list.warningForeground': warn,
        'tree.indentGuidesStroke': guide_act,
        'menu.background': wd_bg, 'menu.foreground': wd_fg, 'menu.selectionBackground': lsel_bg, 'menu.selectionForeground': lsel_fg,
        'menu.separatorBackground': border, 'menu.border': border,
        'menubar.selectionBackground': hover, 'menubar.selectionForeground': on(hover),
        'quickInput.background': wd_bg, 'quickInput.foreground': wd_fg, 'quickInputTitle.background': chrome,
        'quickInputList.focusBackground': lsel_bg, 'quickInputList.focusForeground': lsel_fg,
        'pickerGroup.foreground': ensure(accent, wd_bg, 3.0), 'pickerGroup.border': border,
        'dropdown.background': wd_bg, 'dropdown.foreground': wd_fg, 'dropdown.border': border, 'dropdown.listBackground': wd_bg,
        'input.background': field, 'input.foreground': on(field), 'input.border': border, 'input.placeholderForeground': dim(field, 3.5),
        'inputOption.activeBorder': accent_text, 'inputOption.activeBackground': alpha(accent, 0.3), 'inputOption.activeForeground': NFG,
        'inputValidation.errorBackground': side, 'inputValidation.errorBorder': err,
        'inputValidation.warningBackground': side, 'inputValidation.warningBorder': warn,
        'inputValidation.infoBackground': side, 'inputValidation.infoBorder': info,
        'checkbox.background': field, 'checkbox.foreground': NFG, 'checkbox.border': border,
        'button.background': accent, 'button.foreground': accent_fg, 'button.hoverBackground': blend(accent, far, 0.18),
        'button.secondaryBackground': inact, 'button.secondaryForeground': on(inact), 'button.secondaryHoverBackground': hover,
        'toolbar.hoverBackground': hover, 'toolbar.activeBackground': inact,
        'extensionButton.prominentBackground': accent, 'extensionButton.prominentForeground': accent_fg,
        'extensionButton.prominentHoverBackground': blend(accent, far, 0.18),
        'notifications.background': wd_bg, 'notifications.foreground': wd_fg, 'notifications.border': border,
        'notificationCenterHeader.background': chrome, 'notificationCenterHeader.foreground': on(chrome),
        'notificationLink.foreground': ensure(accent, wd_bg, 3.0),
        'settings.headerForeground': NFG, 'settings.modifiedItemIndicator': accent_text,
    })
    # Terminal (Vims ANSI-Farben)
    ansi = D.get('ansi') or []
    names = ['Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White']
    c.update({'terminal.background': NBG, 'terminal.foreground': NFG, 'terminalCursor.foreground': c.get('editorCursor.foreground', NFG),
              'terminal.selectionBackground': c.get('editor.selectionBackground', alpha(NFG, 0.25)),
              'terminal.border': border, 'terminal.tab.activeBorder': accent_text})
    if len(ansi) == 16:
        for i, n in enumerate(names):
            c['terminal.ansi' + n] = ansi[i]
            c['terminal.ansiBright' + n] = ansi[8 + i]
    return c

def data_name(path, theme):
    n = os.path.basename(path)[4:-len('-color-theme.json')]
    for suf in ('-dark', '-light'):
        if n.endswith(suf): n = n[:-len(suf)]
    for typ in (theme['type'], 'dark', 'light'):       # Vim fordert manche hellen Schemas als 'dark' an
        f = '%s.%s.json' % (n, typ)
        if os.path.exists(os.path.join(DATA, f)): return f
    raise SystemExit('keine Vim-Daten für ' + path)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        s = open(p, encoding='utf-8').read(); t = json.loads(s)
        t['_data'] = data_name(p, t)
        new = build(t)
        del t['_data']
        t['colors'] = new
        open(p, 'w', encoding='utf-8', newline='').write(json.dumps(t, indent=1, ensure_ascii=False) + ('\n' if s.endswith('\n') else ''))
        print(os.path.basename(p), len(new), 'Farben')
