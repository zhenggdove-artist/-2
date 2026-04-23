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

TODO:
- Browser-test a full live artist painting cycle visually after deployment, especially that artists now choose among the 24 rescanned pillars and do not oscillate at walls.
