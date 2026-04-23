Original prompt: Continue Claude's unfinished work on this Three.js urban legend game, focusing on unresolved player/artist model animation issues; user suggested converting FBX models to GLB if easier.

Progress:
- Read CLAUDE.md and confirmed the project is a single-file Three.js game in urban-legend-framework/index.html.
- Preserved Claude's FBX path encoding, mixamorig bone-tail retargeting, and graffiti-height changes.
- Converted Breathing Idle.fbx, Walking.fbx, and painting.fbx to small GLB animation assets in urban-legend-framework/playermodel/.
- Updated index.html to prefer the new GLB animation clips and fallback to FBX if needed.
- Updated late-load artist rewiring so existing artists also receive the real paint animation clip.
- Ran node --check on the module script successfully after edits.
- Ran the develop-web-game Playwright client against a local http.server. It entered gameplay and produced screenshots without console error artifacts; screenshots were cleaned up afterward.

TODO:
- Browser-test a full gameplay run and confirm Shift+X shows artist-idle, artist-walk, and paint with bound track counts instead of ?.
- If visual retargeting still looks wrong, inspect the converted GLB animation node names and compare the first few track names against character.glb bones.
