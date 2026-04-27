# Codex01 Handoff

Last updated: 2026-04-27

## Scope

This handoff covers the recent work in `urban-legend-framework/index.html`, especially the in-browser admin layout editor and HUD/layout changes.

## Current repo state

- Branch: `main`
- Latest known local/remote synced commit when this file was written:
  - `69e0a1f Update index.html`
- Working tree may still contain uncommitted edits after this handoff if later agents continue from here. Re-check `git status` before changing anything.

## Main file

- `urban-legend-framework/index.html`

This project is still a large single-file frontend. Most of the recent work is inside:

- the CSS block near the top
- the `UI_LAYOUT_DEFAULTS` / `UI_LAYOUT_TARGET_DEFS` section
- the admin layout editor JS helpers

## Completed changes

### 1. Loadout / skill card

- The old `BURST FX` card in the loadout bar was replaced by a single skill card.
- It now shows owned weapons/skills instead of burst FX.
- Clicking the skill card cycles to the next owned weapon.

Relevant search terms:

- `weapon-cycle-frame`
- `weapon-cycle-card`
- `getOwnedWeaponIds`
- `cycleOwnedWeapon`
- `renderLoadoutBar`

### 2. Timer frame removed

- The extra editable frame around the timer was removed from:
  - DOM
  - CSS
  - layout target defs
  - layout defaults

Old removed target:

- `timer-box-frame`

### 3. CLEAN button layout support

- `CLEAN` has its own adjustable button target and decorative frame target.
- It is now part of the layout editor target list.

Relevant search terms:

- `clean-btn-frame`
- `body.admin-layout-mode #clean-btn.hidden`

### 4. End screen free camera

- End scene camera now supports:
  - drag to orbit
  - wheel zoom in/out
- Extra end camera state added:
  - `endCameraPitch`
  - `endCameraZoom`

Relevant search terms:

- `endCameraPitch`
- `endCameraZoom`
- `updateCam`

### 5. Viewport frame split into 4 edges

- The big outer frame is no longer a single full-screen overlay.
- It is split into:
  - `viewport-frame-top`
  - `viewport-frame-bottom`
  - `viewport-frame-left`
  - `viewport-frame-right`
- These are individually adjustable in admin mode.

Related assets:

- `urban-legend-framework/img/viewport_frame_top_edge.png`
- `urban-legend-framework/img/viewport_frame_bottom_edge.png`
- `urban-legend-framework/img/viewport_frame_left_edge.png`
- `urban-legend-framework/img/viewport_frame_right_edge.png`

### 6. Admin layout editor clipboard / delete / undo

- Added admin hotkeys:
  - `Ctrl+C`
  - `Ctrl+V`
  - `Delete`
  - `Ctrl+Z`
- Delete currently means soft-hide inside layout config, not removing a target definition.

Relevant search terms:

- `copySelectedUILayoutItem`
- `pasteSelectedUILayoutItem`
- `deleteSelectedUILayoutItem`
- `undoUILayoutChange`
- `handleUILayoutHotkeys`

### 7. Layout Objects panel

- Added a floating `Layout Objects` panel inside admin mode.
- Features already implemented:
  - object list
  - lock/unlock
  - reorder up/down
  - `To Top`
  - `To Bottom`
  - draggable panel
  - resizable panel

Relevant search terms:

- `ui-layout-object-panel`
- `toggleUILayoutLock`
- `moveUILayoutLayer`
- `moveSelectedUILayoutItems`

## Important bug that was fixed

There was a startup-blocking bug introduced by the layout layer logic:

- `getUILayoutDefaultLayer(def)` called `getComputedStyle(el)` even when `el` was `null`
- dynamic targets such as loadout card elements may not exist yet during startup
- this caused a frontend exception during loading and blocked game startup

This was fixed by guarding the missing element case.

Relevant search term:

- `function getUILayoutDefaultLayer`

## Current known problems

### 1. Layout Objects panel selection UX is still unstable

This is the main unresolved area.

User reports:

- `Shift + click` multi-select still does not behave reliably in the panel
- clicking items or `Lock` previously caused the panel list to jump back to the top

Status:

- scroll-jump root cause was partially addressed by separating list rebuild from selection-style refresh
- a helper now exists:
  - `syncUILayoutSelectionStyles`
- but this still needs real browser interaction verification

Likely next focus:

- inspect `pointerdown` / `click` interplay on `.ui-layout-object-row`
- verify `uiLayoutState.selectedIds` changes in live browser
- possibly add temporary debug text showing selected ids

Relevant search terms:

- `selectedIds`
- `syncUILayoutSelectionStyles`
- `refreshUILayoutObjectPanel`
- `row.addEventListener('pointerdown'`
- `row.addEventListener('click'`
- `listDrag`

### 2. Lock should never block underlying selection

Intent:

- a locked item must not be selectable from the on-canvas overlay
- it must not block clicking objects underneath

Current code direction:

- overlay pointer events are disabled when `metrics.locked`

Relevant search term:

- `box.style.pointerEvents=metrics.locked ? 'none' : 'auto'`

This still needs live validation.

### 3. Layout Objects panel reorder behavior needs live testing

Intended behavior:

- panel order defines layer order
- top row = top layer
- bottom row = bottom layer
- multi-selected rows should move together

Code exists, but needs manual verification in browser.

Relevant search terms:

- `applyUILayoutLayerOrder`
- `getUILayoutOrderedIds`
- `moveSelectedUILayoutItems`
- `listDrag`

## Admin mode controls

Current intended controls:

- `Shift+P`: toggle admin layout mode
- `Ctrl+C`: copy selected target metrics
- `Ctrl+V`: paste copied metrics onto selected target
- `Delete` / `Backspace`: hide selected target
- `Ctrl+Z`: undo last editor change

## Layout object panel controls

Current intended controls:

- `Shift + click` rows: add/remove rows from selection
- drag a selected row: reorder selected block in layer stack
- `Lock`: disable on-canvas selection for that target
- `↑` / `↓`: move one target up/down
- `To Top` / `To Bottom`: move selected targets to top/bottom

## Useful code anchors

Search these inside `urban-legend-framework/index.html`:

- `UI_LAYOUT_DEFAULTS`
- `UI_LAYOUT_TARGET_DEFS`
- `sanitizeUILayoutConfig`
- `applyUILayoutMetrics`
- `refreshUILayoutObjectPanel`
- `syncUILayoutSelectionStyles`
- `toggleUILayoutLock`
- `moveSelectedUILayoutItems`
- `handleUILayoutHotkeys`
- `viewport-frame-top`
- `weapon-cycle-card`
- `clean-btn-frame`

## Recommended next steps for next AI

1. Open admin mode in a real browser and test the `Layout Objects` panel directly.
2. Confirm whether `Shift + click` actually updates `selectedIds` live.
3. Confirm panel scroll position stays stable after:
   - clicking rows
   - pressing `Lock`
   - pressing `To Top` / `To Bottom`
4. If multi-select still fails, instrument the row handlers with temporary on-screen debug state instead of guessing.
5. After behavior is confirmed, remove any temporary debug instrumentation and keep the interaction minimal.
