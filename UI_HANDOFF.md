# UI Handoff

Last updated: 2026-04-27

## Purpose

This file is the fast handoff for the ongoing HUD / ornament / layout-editor work in `urban-legend-framework/index.html`.

The project is still a single-file frontend. Most UI state is currently controlled by CSS plus a small in-page layout editor added near the gameplay input code.

## Current branch state

Latest relevant commits before this handoff:

- `6699d48` Adjust HUD alignment and add bar/loadout frame overlays
- `7331f2a` Finish HUD layout and loading font updates
- `43225e6` Add layout admin mode and restore UI framing

There are also two untracked font files in the repo that have **not** been committed:

- `urban-legend-framework/FONTS/Hydrogen Whiskey.otf`
- `urban-legend-framework/FONTS/hyperion.ttf`

`hyperion.ttf` is referenced by CSS now for the loading briefing text, so if a later AI wants the font to work on deploy, that file must actually be added and committed.

## User's intent

The user wants the game HUD to be decorated with their custom PNG frames instead of Claude's earlier yellow traced pseudo-frame approach.

The user also wants a visual admin mode so they can move / resize UI live:

- Desktop edits should affect desktop layout
- Mobile edits should affect mobile layout
- Toggle with `Shift+P`
- Re-toggling should save the layout

Important limitation:

- The current browser-side admin mode can save to `localStorage`
- It cannot directly run local git commands or push to GitHub from the browser
- The current implementation copies JSON layout config to clipboard when possible, but it does **not** rewrite `index.html` automatically

If full "edit in browser then auto-commit to GitHub" is required, it will need a local helper process / local server endpoint / external desktop-side integration.

## Files and assets involved

Main file:

- `urban-legend-framework/index.html`

Current ornament PNGs already generated and committed:

- `urban-legend-framework/img/action_frame_overlay.png`
- `urban-legend-framework/img/viewport_frame_overlay.png`
- `urban-legend-framework/img/paint_bar_frame_overlay.png`
- `urban-legend-framework/img/skill_panel_frame_overlay.png`
- `urban-legend-framework/img/hud_small_frame_overlay.png`

Source images live one folder above repo root and were manually chroma-keyed from green background during previous sessions:

- `../右下按鈕.png`
- `../背景裝飾外框.png`
- `../左側彩虹值bar.png`
- `../技能表.png`
- `../COIN數藝術家數.png`

## What is already implemented

### 1. Right-side action buttons

The `skill / jump / punch` cluster uses the user's custom circular frame PNG.

Relevant CSS area:

- Search for `#special-btn`, `#jump-btn`, `#attack-btn`
- Search for `--action-frame-shift-x`
- Search for `action_frame_overlay.png`

These buttons are positioned by desktop/mobile percentage-based coordinates near the top "Slot centres" block.

### 2. Full viewport decorative frame

Claude's traced yellow full-screen frame was replaced with:

- `img/viewport_frame_overlay.png`

Relevant CSS:

- search `#viewport-frame`

### 3. Paint bar frame

The left vertical paint bar uses:

- `img/paint_bar_frame_overlay.png`

Relevant CSS:

- search `#paint-bar`
- search `#paint-bar::before`

### 4. Small HUD top frames

`artist count`, `timer`, `coin`, `shop` have partially normalized sizing / placement.

Small top HUD frame asset:

- `img/hud_small_frame_overlay.png`

Relevant CSS:

- search `#kill-box,#coin-box,#shop-btn`
- search `#kill-box::before,#coin-box::before,#shop-btn::before`

### 5. Loading font

`BriefingFont` was changed to:

- `FONTS/hyperion.ttf`

Relevant CSS:

- search `@font-face`
- search `BriefingFont`
- search `#intro .tag`
- search `#intro p`

Again: the file is still untracked at time of writing.

### 6. Admin layout mode

`Shift+P` now toggles a layout editor.

What it currently does:

- overlays draggable boxes on major UI pieces
- supports resize using a bottom-right handle
- saves separate config for desktop vs mobile using `window.matchMedia('(max-width:640px)')`
- stores config in `localStorage` under `urbanLegendUILayoutV1`
- attempts to copy JSON to clipboard on save

Relevant JS:

- search `UI_LAYOUT_STORAGE_KEY`
- search `toggleUILayoutEditor`
- search `UI_LAYOUT_TARGET_DEFS`

Relevant CSS:

- search `.ui-layout-editor`
- search `.ui-layout-box`

## Known issues / incomplete work

These are the big remaining problems the next AI should expect:

### 1. Left-bottom loadout frame still needs visual verification

The user explicitly complained that the decorative frame for the bottom-left skill/loadout area disappeared earlier.

Current state:

- `#loadout-bar` no longer owns the big shared decorative frame
- each `.loadout-slot` now gets its own `skill_panel_frame_overlay.png`

This was changed because the user wanted **one frame per skill card**, not one big frame around both cards.

However, after the last code changes, this still needs in-game verification with a clean gameplay screenshot, not just intro-overlay screenshots.

### 2. Paint bar still likely needs pixel-level tuning

The user wanted:

- bar not touching the left edge
- bar fully inside the decorative frame
- spacing similar to their reference image

The code was adjusted, but this still needs real gameplay verification.

### 3. Top HUD layout still likely needs finishing

The user asked for:

- title removed
- timer lower / centered within the top ornament
- `shop`, `coin`, and `artist count` same size
- top-right HUD not colliding with the global background frame

This was partially adjusted, but still needs a proper gameplay screenshot to confirm exact alignment.

### 4. Browser admin mode does not push to GitHub

This is the biggest conceptual gap versus the user's request.

Current implementation:

- save locally
- copy JSON

Not implemented:

- write config back into source file
- run git commit/push from browser interaction

To fully satisfy the user, the next AI will need one of:

1. a local helper script + local HTTP endpoint
2. a desktop-side tool outside the browser
3. a workflow where the user exports JSON and the agent writes it into source code

### 5. Gameplay-state screenshot coverage is still weak

Most recent checks captured intro overlay state, where some HUD is obscured.

The next AI should capture actual gameplay after pressing `BEGIN`, then inspect:

- left paint bar
- left-bottom loadout frames
- top HUD
- right action buttons

## Fast search map

Inside `urban-legend-framework/index.html`, search these tokens:

- `action_frame_overlay.png`
- `viewport_frame_overlay.png`
- `paint_bar_frame_overlay.png`
- `skill_panel_frame_overlay.png`
- `hud_small_frame_overlay.png`
- `UI_LAYOUT_STORAGE_KEY`
- `toggleUILayoutEditor`
- `Shift+P`
- `BriefingFont`
- `#paint-bar`
- `#loadout-bar`
- `.loadout-slot::before`

## Recommended next steps for the next AI

1. Launch the game and get a real gameplay screenshot after pressing `BEGIN`
2. Verify whether the bottom-left loadout cards each show their own frame
3. Fine-tune:
   - `#paint-bar`
   - `#timer-box`
   - `#kill-box`
   - `#coin-box`
   - `#shop-btn`
4. Decide whether to commit `FONTS/hyperion.ttf`
5. If the user insists on browser-triggered GitHub persistence, design a helper workflow instead of pretending browser JS can safely `git push`

## Important behavioral note for future AI

The user wants direct action, minimal excuses, and automatic git push after real progress.

But if asked for impossible browser-side git behavior, be explicit:

- browser can save layout data locally
- agent can write that data back into source and push
- browser page itself cannot reliably and safely perform local git push without extra infrastructure
