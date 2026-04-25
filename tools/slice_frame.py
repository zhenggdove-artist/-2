"""slice_frame.py — slice the full-viewport traced frame SVG into
one sub-SVG per UI region.

Why this exists:
    A single 2730×1536 vine overlay stretched to the live viewport
    can't follow the actual HUD / loadout / button positions across
    desktop AND mobile. Slicing the trace into per-element shards
    lets each shard sit on top of its real UI element via CSS
    background-image, scaling 100 % × 100 % to whatever size the
    live element happens to be on this device.

Usage:
    python tools/slice_frame.py \
        urban-legend-framework/img/frame_traced.svg \
        urban-legend-framework/img

Each region in REGIONS produces a file frame_<name>.svg with paths
translated into the region's local coordinate space.
"""
import re
import os
import sys


# Reference image is 2730 × 1536. Bboxes (x1, y1, x2, y2) approximate
# the locations of each UI cluster in that coordinate space. Tweak
# numbers here to slide a shard up/down/sideways. Order matters
# only in that overlapping regions both keep the contested paths
# (paths whose bounding box intersects multiple regions appear in
# all of them).
REGIONS = {
    "hud_left":     (0,    0,    640,  290),
    "hud_right":    (2090, 0,    2730, 290),
    "title":        (820,  0,    1910, 260),
    "timer":        (1060, 80,   1670, 240),
    "shop":         (2340, 200,  2730, 410),
    "paint_bar":    (0,    140,  220,  1100),
    "loadout":      (0,    980,  840,  1536),
    "title_emblem": (820,  920,  1910, 1536),
    "actions":      (1900, 1020, 2730, 1536),
    # Plain corner shards (for the four screen corners only) — used
    # by #viewport-frame so we still get a thin outer border.
    "corner_tl":    (0,    0,    420,  420),
    "corner_tr":    (2310, 0,    2730, 420),
    "corner_bl":    (0,    1116, 420,  1536),
    "corner_br":    (2310, 1116, 2730, 1536),
}


PATH_RE = re.compile(r'<path d="([^"]+)"/>')
COORD_RE = re.compile(r'([ML])(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)')


def path_bbox(d: str):
    coords = COORD_RE.findall(d)
    if not coords:
        return None
    xs = [float(c[1]) for c in coords]
    ys = [float(c[2]) for c in coords]
    return (min(xs), min(ys), max(xs), max(ys))


def shift_path(d: str, dx: float, dy: float) -> str:
    def repl(m):
        cmd = m.group(1)
        x = float(m.group(2)) - dx
        y = float(m.group(3)) - dy
        return f"{cmd}{x:.0f},{y:.0f}"
    return COORD_RE.sub(repl, d)


def slice_region(paths_d, region):
    x1, y1, x2, y2 = region
    keep = []
    for d in paths_d:
        bb = path_bbox(d)
        if not bb:
            continue
        # Reject paths that lie wholly outside the region.
        if bb[2] < x1 or bb[0] > x2 or bb[3] < y1 or bb[1] > y2:
            continue
        keep.append(f'<path d="{shift_path(d, x1, y1)}"/>')
    return keep, x2 - x1, y2 - y1


def write_region(out_dir: str, name: str, paths, w: float, h: float):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="none">'
        f'<g fill="#fff5a0" fill-rule="evenodd">'
        f'{"".join(paths)}'
        f'</g></svg>'
    )
    target = os.path.join(out_dir, f"frame_{name}.svg")
    with open(target, "w", encoding="utf-8") as f:
        f.write(svg)
    return target, len(svg), len(paths)


def main(svg_path: str, out_dir: str) -> None:
    with open(svg_path, "r", encoding="utf-8") as f:
        text = f.read()
    all_paths = PATH_RE.findall(text)
    print(f"loaded {len(all_paths)} contours from {svg_path}")

    os.makedirs(out_dir, exist_ok=True)
    for name, region in REGIONS.items():
        paths, w, h = slice_region(all_paths, region)
        target, size, n = write_region(out_dir, name, paths, w, h)
        # Avoid the unicode arrow that crashes Windows cp1252 stdout.
        print(f"  {name:14s} {n:4d} paths -> {target} ({size/1024:.1f} kB)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: slice_frame.py <input.svg> <output_dir>"
        )
    main(sys.argv[1], sys.argv[2])
