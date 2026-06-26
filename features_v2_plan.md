# Feature plan (priority)

## 1) Minimize to tray
- Add QSystemTrayIcon + QMenu (Show/Exit)
- Override closeEvent: hide window to tray instead of exiting

## 2) Better loading indicators
- While fetching search results/URLs: show spinner text and disable list interactions
- After URL fetch complete: enable play button and update label

## 3) Keyboard shortcuts (UX improvement)
- Space: play/pause
- Left/Right arrow: previous/next (or seek if focus on slider; optional)
- Ensure shortcuts work even when focus is on search box/list

## 4) Shuffle & Repeat
- Add toggles (Shuffle, Repeat-all / Repeat-one)
- Update next-track selection logic in play_next and auto-next

---
Files to edit:
- ui.py (most UI/logic)
- main.py (optional: tray/icon init if needed)
- styles.py (optional new styling for toggle buttons/labels)


