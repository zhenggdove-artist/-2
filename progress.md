Original prompt: Continue Claude's unfinished work on this Three.js urban legend game, focusing on unresolved player/artist model animation issues; user suggested converting FBX models to GLB if easier.

Progress:
- Read CLAUDE.md and confirmed the project is a single-file Three.js game in urban-legend-framework/index.html.
- Preserved Claude's FBX path encoding, mixamorig bone-tail retargeting, and graffiti-height changes.
- Converted Breathing Idle.fbx, Walking.fbx, and painting.fbx to small GLB animation assets in urban-legend-framework/playermodel/.
- Updated index.html to prefer the new GLB animation clips and fallback to FBX if needed.
- Updated late-load artist rewiring so existing artists also receive the real paint animation clip.
- Ran node --check on the module script successfully after edits.
- Ran the develop-web-game Playwright client against a local http.server. It entered gameplay and produced screenshots without console error artifacts; screenshots were cleaned up afterward.
- User reported artists still T-posing/sliding and paint not playing. Root cause found: the first Blender batch left old actions in bpy.data, so the exported GLBs could contain previous clips and load the wrong first animation.
- Re-exported artist_idle.glb, artist_walk.glb, and paint.glb from a clean Blender scene per file. Each GLB now contains exactly one animation.
- Replaced bbox-only graffiti placement with a wall-surface raycast. Small meshes use DecalGeometry; large merged meshes use a plane flush to the hit point and normal.
- Browser probe confirmed idle/walk/paint clips all bind 130/130 tracks after the clean GLB export.
- User reported artists still reversing into walls and only a few columns accepting graffiti. Confirmed root cause: pillar detection was failing and falling back to 8 synthetic circle positions (`[playground] loaded ... pillars=8`), so most artists were targeting fake columns.
- Added a post-floor-selection geometry rescan that raycasts the real merged playground mesh and rebuilds up to 24 pillar targets from actual wall hits.
- Split artist state handling so `leave` is no longer overwritten by `walk`, and replaced the hard 180-degree bump response with persistent escape steering chosen by local free-space scoring.
- Added a shop UI, equipment/loadout bar, and cleaner economy. Cleaners cost 1 coin for 3 uses and can remove nearby graffiti while reducing the paint bar by one filled pillar.
- Added purchasable knockout burst effects (5 coins each) plus a default amber burst; equipped effect is switched from the new bottom-left loadout bar and plays on artist KO.
- Added a retry button to the ART WINS overlay and a contextual CLEAN button / E key interaction near graffiti.
- Tuned artists so painting takes 10 seconds, walk-speed halves when they are farther than 10m from the player, and ART WINS now requires 15 filled pillars.
- Simplified the ART WINS overlay visuals to text-only over the existing fade layer and throttled clean-target scanning to reduce per-frame hitches.
- Added a scrollable shop panel so lower cards are reachable on smaller screens.
- Expanded purchasable KO burst effects with fire, ice, and tornado variants and exposed them in the loadout bar.
- Added purchasable special gear: flamethrower, shadow clone, and bomb trap, plus a new special-skill button beside SWING and `Q/K` keyboard trigger.
- Added Shift+C test mode: unlocks all bursts/weapons/cleaner uses, freezes the timer, suppresses ART WINS, and keeps the paint bar in test state.
- Browser-tested with Playwright against a local http.server after load: shop scroll reached the bottom (`shopScroll` ~628), the bomb purchase button had a visible rect, loadout expanded to 11 slots under test mode, timer showed infinity, paint bar showed TEST, and there were no page/console errors.
- Generated `mainplayermodel/player_main.glb`, `player_run.glb`, `player_jump.glb`, `player_punch.glb`, `player_fire.glb`, and `player_throwbomb.glb` from the user's FBX action set with Blender 4.3.
- Switched the player loader to use the new `mainplayermodel` GLBs instead of `character.glb`, changed the attack button/text from SWING to PUNCH, and wired player punch/fire/throw-bomb one-shot animations into gameplay.

TODO:
- Tune the new special weapons if the user wants stronger or more tactical behavior; current versions prioritize low-risk implementation and stable frame-time.
- If needed, clean up a few mojibake shop labels caused by the source file's mixed encoding history.

- Re-exported mainplayermodel/player_kick.glb, player_punchcombo.glb, and replaced player_jump.glb from the user's new FBX actions using armature-only GLB export so the files stay lightweight.
- Updated player combat to rotate attacks in order: punch -> kick -> combo, with per-clip one-shot timing instead of a single fixed punch duration.

- Replaced mainplayermodel/player_run.glb with a lightweight armature-only export from mainplayermodel/action/Fast Run.fbx so the player's run animation uses the new fast-run clip without increasing runtime asset cost.

- Reworked player attack input toward tap/hold semantics: short tap schedules punch, long hold triggers kick, and a second quick tap upgrades the pending hit to combo. Also cut player speed by 20% while attacking/holding attack and snap run->idle immediately when movement input stops to reduce visible foot-sliding.
- Converted burst FX progression from shop purchases to KO-based unlocks in code (10/20/30 kills for snowflake/hexagram/heart) and hid unsupported legacy burst shop cards. Startup now defers coin loading and schedules river scanning asynchronously instead of putting both on the critical path.
- Added lightweight `mainplayermodel/player_clean.glb` from `action/Clean.fbx`, wired clean requests to play the clean animation first, and included `actClean` in the one-shot reset logic so the player returns to idle instead of freezing on a tail frame.
- Tightened the single-tap punch subclip further so only the middle "real" punch section remains, and generalized player one-shot playback so throw-bomb can be sped up safely.
- Changed bomb behavior so the throw animation plays at 1.7x speed, the bomb object appears only after the animation completes, it auto-detonates after 10 seconds, and the blast uses a 5x5-area mushroom cloud particle effect.
- Added localStorage caches for playable-layer and river detection to reduce repeat startup scan time. A fresh Playwright smoke run still found `#start-btn` disabled after the client's 5s click timeout, so first-load startup is better but not solved yet.
- Added camera-to-player roof occlusion fading: overhead ceiling meshes that block the camera ray now fade to semi-transparent and restore automatically when the line of sight clears.
- Replaced the unstable built-in player idle with a lightweight `mainplayermodel/player_idle.glb` exported from `action/Idle.fbx`, and stopped re-resetting idle every frame so the player no longer T-poses/shivers while standing still.
- Moved both floor scanning and artist-template loading off the initial blocking path. Current browser probe shows `#start-btn` returns to `BEGIN` and becomes enabled within ~3 seconds on first load instead of staying stuck disabled.
- Player textures are now loaded in the background after the base player model/animations, so the game can enter sooner and the mesh gets detailed materials once they finish.
- Replaced the player idle source again using `mainplayermodel/action/Neutral Idle.fbx` exported as a lighter `player_idle.glb`, and sanitized player clips with the same hip/root position-track stripping used for artists. This is aimed at the stop->sink->T-pose hitch when switching from run to idle.
- Added stronger idle/run recovery helpers so stopping movement no longer depends only on `isRunning()`; if idle is technically running but at near-zero weight, it now gets faded back in instead of leaving the player with no meaningful clip influence.
- Reduced mid-game overhead further by updating KO burst particles only for active particle indices instead of scanning the full `KO_MAX` pool every frame, and throttled the roof-occlusion raycast to every few frames.
- Ice block visuals now use a 3D hexagonal prism silhouette instead of a cube.
- Reduced first-load blocking again by removing the old `character.glb` / `coin.glb` preloads, loading only player base mesh + idle/run + basecolor on the critical path, and deferring jump/punch/kick/combo plus the rest of the player maps to the background loader.
- Added mobile-specific loadout UX: a new `GEAR` toggle button now appears above the lower-left controls on small screens, the full loadout bar is collapsed by default on mobile, and tapping the toggle expands a smaller horizontal equipment strip raised above the action buttons.
- Strengthened mobile HUD layout so the loadout strip sits higher and no longer stacks directly on top of the joystick / jump / punch row; active loadout state remains visually highlighted.
- Centered the `ART WINS` text block more defensively for mobile by forcing centered alignment and a bounded width on the overlay text.
- Verified via a narrow Playwright viewport script that on mobile the intro can be skipped programmatically, `#loadout-toggle` is visible, the loadout bar starts with `opacity: 0` / `pointer-events: none`, and after toggling the body gains `loadout-open` and the bar becomes interactive near the bottom-middle of the viewport.
- Standard `develop-web-game` client still did not complete cleanly this round: it timed out trying to click `#start-btn` even though the button text had already returned to `BEGIN`. Intro overlay non-button content now has `pointer-events: none` and the start button has explicit `pointer-events: auto`, but this startup-click flake still needs another pass.
- Mobile controls were re-laid out again after user screenshot feedback: `SKILL` now sits directly above `PUNCH`, and the lower-left `GEAR` toggle remains separate from the joystick so the three touch clusters no longer overlap on a 390px-wide viewport.
- Added page-level long-press / selection hardening for the game UI: body text is now non-selectable by default, inputs remain selectable, and `selectstart` plus `contextmenu` are prevented so mobile long-press no longer highlights text over the game.
- Added a visible intro loading progress bar (`BOOT / ASSETS / READY / STREAM`) with percentage text. The initial ready state now reaches ~74% once the game is playable, then continues toward 100% as background floor/river/character streaming completes.
- Reduced mobile GPU cost further by switching to `antialias:false` on coarse/mobile layouts, lowering renderer pixel ratio to 1.0 on mobile, halving water-shader updates to every other frame on mobile, increasing ceiling-occlusion throttling, and reducing death-flower spawn/cap on mobile.
- Deferred `coin.glb` loading out of the startup critical path via `requestIdleCallback`/timeout. Coin fallback meshes still work if the GLB hasn't finished streaming yet.
- Reworked artist leave targets to use explicit exit points outside the arena (`pickExitPos`) instead of reusing spawn points. Leave-state artists now only despawn once they actually reach or pass the arena edge, and if they get stuck they retarget another exit instead of vanishing in-place.
- Manual mobile Playwright probe on 390x844 confirms: intro progress text renders, start button becomes enabled, `SKILL` sits above `PUNCH`, and the lower-left `GEAR` button is separated from the joystick cluster.
- User reported the previous exit-target change was too aggressive and caused artists to leave the map / jitter upward. Leave logic has now been simplified back to a safe "run to inner wall, then despawn" path: `pickExitPos()` now chooses a point just inside the playable bounds, leave-state movement uses the existing clamped movement path again, and artists are removed only once they reach that wall target or stay stuck for too long.
- Added a simpler "air-wall first" safety approach by keeping all leave motion inside the same clamp system as every other movement state. This intentionally prefers boring but stable behaviour over cinematic exits.
- Startup/perf tuning continued: mobile still uses lower pixel ratio, no antialiasing, water updates every other frame, and flower spawn/cap are reduced. `coin.glb` remains deferred off the startup critical path.
- Narrow-view probe after the latest fixes still confirms the mobile control stack is separated (`SKILL` above `PUNCH`) and the intro progress text advances during streaming.
- Mobile loadout toggle was moved farther right so it no longer overlaps the rainbow paint bar, and it is now a blue circular button using a clothing icon instead of text.
- Artist population tuning was tightened to reduce both clutter and CPU cost: the live cap is now 5, and when the active count drops to 3 or below the spawn timer shortens so replacements appear quickly.
- Performance was reduced more aggressively on mobile: the VHS/composer pass is skipped entirely during gameplay rendering, and heavy `coin.glb` loading is bypassed on mobile in favor of the lightweight fallback coin mesh.
- User rejected the previous visual downgrade. Restored the original post-process / scene presentation by re-enabling the composer+VHS render path on mobile again and restoring normal `coin.glb` loading; kept only the functional mobile UI position fix for the loadout button.
- Loadout toggle icon is now a simple pure-white shirt silhouette (mask-based icon), with no text or interior detail, while staying in the moved-right blue circular button position.
- Attack movement slowdown was relaxed from 10% back to 20% so the player can keep drifting in the pressed direction during punch/skill actions as requested.
