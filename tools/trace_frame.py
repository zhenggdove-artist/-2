"""trace_frame.py — extract the neon-yellow ornaments from the
design reference image and emit an SVG that the game can wear as
a real vector frame.

Why this exists:
    Hand-coding SVG paths to mimic the reference produced ugly
    approximations because there was no visual feedback loop. The
    only honest way to "completely copy" the reference (per the
    user's brief) is to actually trace the bitmap and use its
    real shape data. cv2.findContours gives us proper polygon
    outlines that we then format as SVG <path>.

Usage:
    python tools/trace_frame.py <input.png> <output.svg>
"""
import sys
import os
import cv2
import numpy as np


def trace(input_path: str, output_path: str) -> None:
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit(f"could not read {input_path!r}")
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    h, w = img.shape[:2]

    # Convert BGR → HSV. Neon yellow-green in the ref centres around
    # H ≈ 30° (in 0-179 OpenCV scale that's 15) with very high V.
    # Pull a generous band so we capture the soft-glow halo too.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Two yellows to be safe: pure neon (warmer) and yellow-green.
    mask_yellow = cv2.inRange(hsv, (18, 60, 170), (40, 255, 255))
    mask_green = cv2.inRange(hsv, (35, 30, 170), (60, 255, 255))
    mask = cv2.bitwise_or(mask_yellow, mask_green)

    # Clean up: dilate to merge fragmented strokes, then close.
    k = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)
    mask = cv2.dilate(mask, k, iterations=1)
    # Drop tiny noise specks.
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_TC89_KCOS)
    contours = [c for c in contours if cv2.contourArea(c) >= 35]

    # Build SVG. Each contour becomes one <path> with M/L commands.
    # Round to 1 decimal for a smaller file and acceptable fidelity
    # at the sizes we render — anything tighter is wasted bytes.
    paths = []
    for c in contours:
        pts = c.reshape(-1, 2)
        if len(pts) < 3:
            continue
        d_parts = [f"M{pts[0,0]:.0f},{pts[0,1]:.0f}"]
        for x, y in pts[1:]:
            d_parts.append(f"L{x:.0f},{y:.0f}")
        d_parts.append("Z")
        paths.append(
            f'<path d="{"".join(d_parts)}"/>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
        f'<g fill="#fff5a0" fill-rule="evenodd">'
        f'{"".join(paths)}'
        f'</g></svg>'
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(
        f"traced {len(paths)} contour(s) "
        f"({len(svg) / 1024:.1f} kB SVG) → {output_path}"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: trace_frame.py <input.png> <output.svg>")
    trace(sys.argv[1], sys.argv[2])
