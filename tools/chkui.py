#!/usr/bin/env python3
"""chkui.py <theme.json> ... -- Kontrast der Oberflächenfarben (Schrift gegen Hintergrund), schwächste Paare je Theme."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkui import contrast
PAIRS = [('foreground', 'editor.background', 4.5), ('sideBar.foreground', 'sideBar.background', 4.5),
 ('activityBar.foreground', 'activityBar.background', 4.5), ('activityBar.inactiveForeground', 'activityBar.background', 3.0),
 ('titleBar.activeForeground', 'titleBar.activeBackground', 4.5), ('titleBar.inactiveForeground', 'titleBar.inactiveBackground', 3.0),
 ('tab.activeForeground', 'tab.activeBackground', 4.5), ('tab.inactiveForeground', 'tab.inactiveBackground', 4.5),
 ('statusBar.foreground', 'statusBar.background', 4.5), ('statusBar.debuggingForeground', 'statusBar.debuggingBackground', 4.5),
 ('statusBarItem.remoteForeground', 'statusBarItem.remoteBackground', 4.5), ('list.activeSelectionForeground', 'list.activeSelectionBackground', 4.5),
 ('list.hoverForeground', 'list.hoverBackground', 4.5), ('menu.foreground', 'menu.background', 4.5),
 ('menu.selectionForeground', 'menu.selectionBackground', 4.5), ('editorSuggestWidget.foreground', 'editorSuggestWidget.background', 4.5),
 ('editorSuggestWidget.selectedForeground', 'editorSuggestWidget.selectedBackground', 4.5), ('button.foreground', 'button.background', 4.5),
 ('badge.foreground', 'badge.background', 4.5), ('input.foreground', 'input.background', 4.5),
 ('notifications.foreground', 'notifications.background', 4.5), ('editorWidget.foreground', 'editorWidget.background', 4.5),
 ('editorError.foreground', 'editor.background', 3.0), ('editorWarning.foreground', 'editor.background', 3.0),
 ('focusBorder', 'editor.background', 3.0), ('tab.activeBorderTop', 'tab.inactiveBackground', 3.0)]
bad = 0; worst = {}
for p in sys.argv[1:]:
    c = json.load(open(p, encoding='utf-8'))['colors']; n = os.path.basename(p)[4:-len('-color-theme.json')]
    for fg, bg, need in PAIRS:
        if fg not in c or bg not in c: print('FEHLT', n, fg, bg); bad += 1; continue
        r = contrast(c[fg], c[bg])
        if r < worst.get((fg, bg), (99, ''))[0]: worst[(fg, bg)] = (r, n)
        if r < need - 0.01: print('zu niedrig: %-22s %-42s %.2f < %.1f' % (n, fg + ' auf ' + bg.split('.')[0], r, need)); bad += 1
print('Paare unter Soll:', bad)
for (fg, bg), (r, n) in sorted(worst.items(), key=lambda x: x[1][0])[:6]: print('  knappster Wert: %.2f  %s / %s (%s)' % (r, fg, bg, n))
