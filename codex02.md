# Codex02 Handoff

Last updated: 2026-04-27

## Scope

This file is the latest AI handoff for the current state of the project in `都市傳說2/`.
It consolidates:

- current repo status
- earlier notes from `codex01.md`, `UI_HANDOFF.md`, and `progress.md`
- the most likely next work area for the next AI session

## Repo status

- Active repo root: `都市傳說2/都市傳說2`
- Main gameplay file: `urban-legend-framework/index.html`
- Current branch: `main`
- Working tree status when this file was written: clean
- `urban-legend-framework/index.html` size at handoff: about 371 KB

Recent commits:

- `d5c6122` `Polish mobile layout admin and paint bar`
- `28cf486` `Refine admin overlay selection and resize handles`
- `98cf6b0` `Update UI layout defaults and editor handles`
- `78c535e` `Update index.html`

## Project shape

This is still effectively a single-file Three.js game.

Key locations:

- `urban-legend-framework/index.html`: gameplay, UI, CSS, layout editor, Supabase flow
- `urban-legend-framework/img/`: custom HUD / frame overlays
- `urban-legend-framework/mainplayermodel/`: player GLB animations
- `urban-legend-framework/playermodel/`: artist GLB animations and older source assets
- `urban-legend-framework/field/playground_optimized.glb`: preferred arena model
- `supabase/leaderboard_schema.sql`: leaderboard schema with `scene_state`
- `tools/`: helper scripts used in past UI/image tracing work

## Already in place

### Gameplay / systems

- Player now uses dedicated GLB animation assets instead of the original shared `character.glb` set for key actions.
- Attack chain supports punch / kick / combo with tap-hold logic.
- Clean action has its own animation.
- Special gear exists: flamethrower, shadow clone, bomb trap.
- KO burst effects are unlock/equip driven and include multiple variants.
- Artists use repaired GLB animation clips and safer movement / leave logic than earlier broken versions.
- Graffiti placement uses wall-surface raycasts instead of simple bbox placement.
- Endgame leaderboard submission includes serialized `scene_state`, and leaderboard rows can preview stored final scenes.

### Performance / loading

- Startup work has been reduced multiple times to get `BEGIN` enabled sooner.
- Playground now prefers `field/playground_optimized.glb` and falls back to the older file if needed.
- Some expensive scans and BVH-related work were moved off the initial blocking path or sliced into background work.
- Several low-risk runtime optimizations already exist for coins, roof occlusion, particles, and audio playback.

### UI / HUD / layout editor

- User-supplied frame art has replaced the older traced placeholder look in major HUD areas.
- Admin layout mode exists and toggles with `Shift+P`.
- Layout editor supports draggable / resizable targets, separate mobile-vs-desktop configs, clipboard copy/paste, delete, undo, lock, and layer ordering tools.
- A floating `Layout Objects` panel exists for selection, reordering, and locking.
- Mobile loadout UX now uses a separate circular `E` toggle button and a collapsible loadout strip.

## Important current truth

The biggest active area is not raw feature implementation. It is verification and cleanup of the UI layout editor behavior and final HUD alignment.

Earlier notes strongly suggest the code exists, but some interactions were only partially validated in browser.

## Highest-priority unresolved items

### 1. Layout Objects panel still needs live browser verification

This is the most likely next AI task.

Known concerns from earlier handoff:

- `Shift+click` multi-select may still be unreliable
- row click / lock / reorder may still cause scroll jump or selection instability
- locked items should not block selecting items underneath on the canvas
- layer reorder behavior needs real interaction testing, not just code inspection

Search anchors:

- `refreshUILayoutObjectPanel`
- `syncUILayoutSelectionStyles`
- `toggleUILayoutLock`
- `moveSelectedUILayoutItems`
- `handleUILayoutHotkeys`
- `selectedIds`

### 2. HUD placement still needs gameplay-state visual QA

Areas previously reported as needing real screenshots during gameplay:

- bottom-left loadout card frames
- left paint bar spacing inside its ornament
- top HUD alignment for timer / coin / artist count / shop
- right-side action button cluster

This should be verified after pressing `BEGIN`, not only on the intro screen.

### 3. Browser-side layout editing still does not persist to source control by itself

Current behavior:

- saves to `localStorage`
- may copy layout JSON to clipboard

Not implemented:

- writing layout JSON back into `index.html`
- committing or pushing changes automatically from the browser

If the user asks for browser edits that persist to GitHub, the next AI will need to bridge that from the local workspace side.

## Useful files to read first next time

- `codex01.md`
- `UI_HANDOFF.md`
- `progress.md`
- `CLAUDE.md`
- `urban-legend-framework/index.html`

## Recommended next-session plan

1. Run `git status` and `git log --oneline -10` again before editing.
2. Open the game in a real browser and enter gameplay.
3. Test admin mode with `Shift+P`.
4. Verify `Layout Objects` panel behavior directly:
   - single select
   - `Shift+click` multi-select
   - lock/unlock
   - reorder up/down
   - `To Top` / `To Bottom`
   - drag reorder
5. Capture actual gameplay screenshots for HUD alignment.
6. Only after browser validation, adjust CSS / layout defaults / panel logic in `urban-legend-framework/index.html`.

## Quick search map

Search these inside `urban-legend-framework/index.html`:

- `UI_LAYOUT_DEFAULTS`
- `UI_LAYOUT_TARGET_DEFS`
- `UI_LAYOUT_STORAGE_KEY`
- `toggleUILayoutEditor`
- `refreshUILayoutObjectPanel`
- `syncUILayoutSelectionStyles`
- `viewport-frame-top`
- `weapon-cycle-card`
- `clean-btn-frame`
- `loadout-toggle`

## Notes for the next AI

- The outer folder is not the git repo; the actual repo root is the inner `都市傳說2` directory.
- Do not assume old CLAUDE-era notes about counts/timers/goals are still exact; several gameplay values were changed later in `progress.md`.
- Existing documentation is useful, but `progress.md` contains the broadest change history and is newer than `codex01.md` for many gameplay systems.
- If making any `index.html` edits, run a syntax check before finishing.
