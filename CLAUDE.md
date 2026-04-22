# CLAUDE.md — Project Briefing

> Read this first. Skip the re-discovery phase.

## What this is

A browser 3D game built on Three.js, everything in ONE file:
`urban-legend-framework/index.html` (~3150 lines, inline `<script type="module">`).

Concept: **DEFEND YOUR HOME**. The player is the keeper of an abandoned
playground. Rude graffiti artists spawn at the edges, walk to pillars
and paint on them. The player has a club and swings to knock them
down. Each defeated artist blooms 3 plants and drops a coin. 3-minute
round. On the left is a hot-pink "home lifeblood" bar that gets
overwritten with rainbow paint — 10 completed pillars ends the game
with an **ART WINS** fade-to-black.

There's no separate build step. The HTML is hosted directly by the
user (auto-deploys from GitHub main). Test by opening the file or
pushing to `main`.

## Where things live

- `urban-legend-framework/index.html` — everything. HTML + CSS + JS.
- `urban-legend-framework/character.glb` — player & artist model
  (shared via SkeletonUtils.clone; artists get a reddish tint). Also
  contains `idle`, `walk`, `run`, `jump` animation clips.
- `urban-legend-framework/coin.glb` — coin model.
- `urban-legend-framework/field/playground.glb` — THE arena (17MB,
  multi-story model). Player plays on the **middle layer** (detected
  by `detectPlayableLayer`), NOT the rooftop.
- `urban-legend-framework/playermodel/主角/*.fbx` — auxiliary
  animations loaded after game start. `painting.fbx` → `clipPaint`
  (played when artists paint). `Running.fbx` was tried as
  `clipPanicRun` but retargets poorly, so we don't use it.
- `urban-legend-framework/music/4月2日.MP3` — BGM.
- `urban-legend-framework/FONTS/` — GoldenGirdle + others.
- `CLAUDE.md` — this file.
- `index.html` at repo root is just a redirect to
  `urban-legend-framework/index.html`.

## Dependencies (via ES-module CDN imports)

- `three@0.160.0` (core + addons: GLTFLoader, DRACOLoader, FBXLoader,
  SkeletonUtils, EffectComposer, RenderPass, ShaderPass,
  DecalGeometry).
- `three-mesh-bvh@0.7.5` (loaded dynamically, `bvhReady` flag). This
  is CRITICAL — without it, raycasts on the 17MB playground are
  unusably slow. If it fails to load we fall back to flat ground
  (getGroundY returns 0).

## Collaboration context

- User splits dev between **Claude Code** (me) and **Codex**. Both
  edit the same `index.html`. Always `git status` / `git log` at the
  start of a session to see what's changed on disk.
- User tests by hard-refreshing their browser. If they say "doesn't
  work", it's usually either stale cache OR a real bug — ask them to
  share console output before assuming the cache.
- User writes feedback in **Traditional Chinese**. Tone is often
  blunt. Take it at face value and fix, don't get defensive.
- Supabase (`defender_leaderboard` table, project
  `ztpftxwfcppsqosilssq`) stores 3-min-score leaderboard. If the
  table doesn't exist, game silently falls back to localStorage cache.

## Game state machine

`gameState` values: `'intro' | 'playing' | 'ended' | 'artWins'`.

- `intro` → user clicks START → `startGame()` → `playing`
- `playing` → timer hits 0 → `endGame()` → `'ended'` (leaderboard)
- `playing` → 10 pillars filled → `triggerArtWins()` → `'artWins'`
  (fade to black + big title)

`tick()` only runs gameplay updates when `gameState === 'playing'`.
Rendering always proceeds.

## Core systems overview

- **Player** (`player` object ~line 1930): movement, jump (Space or
  JUMP button), attack (F/J/SWING button), third-person camera.
  Club is a mesh attached to player.root at a fixed hip offset (NOT
  bone-attached — bone retargeting was unreliable).
- **Artists** (`artists` array): state machine `walk|paint|flee|leave|dying`.
  `artistTransition(a, state)` handles animation fades. Flee uses the
  GLB's built-in `run` clip at 1.35× timeScale — don't reintroduce
  the `panic-run` FBX, it retargets badly and produces face-plants.
- **Pillars** (`pillars` array): detected heuristically by name
  regex or tall-and-narrow bbox. `pillar.mesh` is a reference to the
  actual GLB mesh; `pillar.pos` is world-space bbox-center.
- **Graffiti** (`getOrCreateGraffitiPlane`): raycasts from the
  artist's eye in their facing direction, uses hit point + flattened
  face normal. DecalGeometry is tried if the target mesh has ≤18k
  triangles; otherwise a plane flush with the hit is used. Progress
  is baked into a canvas texture that's progressively redrawn.
- **River** (`RIVERS` array, `detectRiverBounds`): samples the
  playable layer for lowest-20% cells, splits into left-of-center
  and right-of-center bands. Each band stretches the full arena Z
  length to stay continuous. Water surface uses a custom
  ShaderMaterial with 3-octave value-noise + 8-stop blue palette.
- **Coins / flowers / splashes**: all capped (30 / 120 / 400) to
  bound memory.

## Tuning knobs (search for these constants)

Gameplay:
- `COIN_SCALE` (~L2400) — coin size. History: 40→4→0.2→0.6.
- `ARTIST_PAINT_TIME` (~L1998) — seconds to complete a pillar (currently 3).
- `ARTIST_SPAWN_BASE` (~L1999) — seconds between spawns at start.
- `ARTIST_MAX_ALIVE` (~L2000) — cap concurrent artists.
- `GAME_DURATION` (~L2848) — round length (180s).
- `PAINT_FILL_GOAL` (~L2853) — pillars needed for ART WINS (10).
- `PLAYER_MAX_SPEED` / `PLAYER_ACCEL` / `PLAYER_DECEL` (~L1952).
- `JUMP_VEL` / `GRAVITY` (~L1959).
- `ATTACK_RANGE` / `ATTACK_ARC` / `ATTACK_DUR` / `ATTACK_COOLDOWN`
  (~L1955).
- `WATER_SPEED_MULT` (~L1961) — 0.8 slowdown when wading.

Geometry / raycasting:
- `GROUND_Y_OFFSET` (~L728) — foot-lift above ground (0.05).
- `groundYCache` — 0.5m-grid cache keyed by `kx*100000+kz`, cap 6000
  with LRU eviction.

Water shader:
- Ramp stops and noise weights are in the fragment shader inside
  `createWaterMesh` (~L1035). Search for `ramp(float t)` and the
  3-octave `vnoise`.

## Performance cliffs we've hit (don't reintroduce these)

1. **Per-frame raw raycast**. `getGroundY`/`getStandY` MUST go
   through `cachedRayY`. A previous pass called `rayGroundY()`
   directly and dropped framerate to 10fps.
2. **`groundRaycaster.firstHitOnly=false` globally**. Must be true
   at runtime. `rayGroundHits` toggles it to false for one call then
   restores. If you leave it false, BVH speedup is gone.
3. **DecalGeometry on huge meshes**. Gate by target triangle count
   (currently ≤18000). Beyond that, use the flat plane fallback —
   building the decal iterates every triangle of the target mesh
   synchronously.
4. **BVH build with default SAH strategy**. Use `CENTER` strategy
   with `maxLeafTris:20` — saves ~10s at load.
5. **`liftCeilingGeometry` rebuilding BVH**. Dispose the old tree,
   do NOT compute a new one. Also skip `computeVertexNormals`.
6. **Disposing shared geometry**. SkeletonUtils.clone SHARES
   geometry across artist instances. Disposing the first clone's
   geometry breaks all subsequent clones. Only dispose per-instance
   cloned materials.
7. **Clearing the whole groundYCache at cap**. Use LRU single-entry
   eviction, not `.clear()`. Mass clear causes a visible frame spike
   when the next frame has to re-raycast everything.

## Common bug patterns

- **Character sinks into floor** → `getStandY` cache missed AND the
  sample fallback is inaccurate. Keep the 3-tier fallback intact.
- **Graffiti floats in the air** → raycast hit a floor/ceiling
  instead of a wall. Filter hits by `|normal.y| > 0.6` and skip.
- **Artists face-plant / crawl during flee** → someone reintroduced
  `I.root.rotation.x = Math.PI*0.5` or the panic-run FBX is being
  used. Keep rotation.x at 0 and play `actRun` with timeScale 1.35.
- **Water looks like 2 solid blue blocks** → vertex-color
  interpolation is too sparse; fragment shader must do per-pixel
  ramp sampling. Don't revert to per-vertex.
- **Mobile HUD overlaps title** → CSS `@media (max-width:640px)`
  block that pushes the title to `bottom:46vh` and shrinks
  `.hud-box` font. Don't remove it.

## Quick self-test

Before shipping any change, in the browser console you should see:
```
[bvh] loaded
[char] loaded, anims: [idle, walk, run, jump]
[playground] loaded. scale=... pillars=X worldR=...
[ground] meshes for raycast: N
[bvh] built for ... meshes
[river] detected: [{...}, {...}]
```
If BVH is missing, everything will feel slow. If river is null, the
trench detection failed — probably the playable-layer sampling
couldn't find enough low-samples.

## Git flow

- Branch: `main` (no PRs — user pushes directly).
- Commit message style: short imperative subject + detailed body.
  Include `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`.
- After every real change, `git push origin main`. User auto-deploys
  from main. Don't rebase or force-push — user's other editor
  (Codex) may have unpushed work.
- Always read `git status` and `git log -5` at start of session.

## Session-start checklist

1. `git status` + `git log --oneline -10` — see what Codex did.
2. Read CLAUDE.md (this file).
3. If the user reports a bug, ask for console output before
   speculating.
4. For any edit to `index.html` run the quick syntax check:
   ```
   node -e "const fs=require('fs');const s=fs.readFileSync('urban-legend-framework/index.html','utf8');const m=s.match(/<script type=\"module\">([\s\S]*)<\/script>/);fs.writeFileSync('/tmp/_c.mjs',m[1].replace(/^\s*import.*?;\s*$/gm,''))" && node --check /tmp/_c.mjs
   ```
5. Commit + push when done. If BGM / textures don't refresh for the
   user, remind them to hard-refresh (Ctrl+Shift+R).
