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

TODO:
- Tune the new special weapons if the user wants stronger or more tactical behavior; current versions prioritize low-risk implementation and stable frame-time.
- If needed, clean up a few mojibake shop labels caused by the source file's mixed encoding history.
