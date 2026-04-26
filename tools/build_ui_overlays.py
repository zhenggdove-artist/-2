from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT.parent
OUT_DIR = ROOT / "urban-legend-framework" / "img"


def chroma_key(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    out = Image.new("RGBA", img.size)
    src = img.load()
    dst = out.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            green_gap = g - max(r, b)
            if g > 70 and green_gap > 22:
                alpha = max(0, min(255, 255 - green_gap * 9))
                if alpha < 18:
                    dst[x, y] = (0, 0, 0, 0)
                    continue
                dst[x, y] = (r, min(g, max(r, b) + 10), b, alpha)
                continue
            dst[x, y] = (r, g, b, a)
    return out


def crop_to_alpha(img: Image.Image, pad: int = 0) -> Image.Image:
    bbox = img.getbbox()
    if not bbox:
        return img
    left = max(0, bbox[0] - pad)
    top = max(0, bbox[1] - pad)
    right = min(img.width, bbox[2] + pad)
    bottom = min(img.height, bbox[3] + pad)
    return img.crop((left, top, right, bottom))


def build_one(src_name: str, out_name: str, pad: int = 10) -> None:
    src = SRC_DIR / src_name
    out = OUT_DIR / out_name
    img = Image.open(src)
    img = chroma_key(img)
    img = crop_to_alpha(img, pad=pad)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"built {out_name}: {img.size}")


def main() -> None:
    jobs = [
        ("\u80cc\u666f\u88dd\u98fe\u5916\u6846.png", "viewport_frame_overlay.png", 8),
        ("\u53f3\u4e0b\u6309\u9215.png", "action_frame_overlay.png", 10),
        ("\u5de6\u5074\u5f69\u8679\u503cbar.png", "paint_bar_frame_overlay.png", 8),
        ("\u6280\u80fd\u8868.png", "skill_panel_frame_overlay.png", 10),
        ("SHOP\u88dd\u98fe\u6846.png", "hud_small_frame_overlay.png", 10),
        ("COIN\u6578\u85dd\u8853\u5bb6\u6578.png", "hud_coin_shop_frame_overlay.png", 10),
    ]
    for src_name, out_name, pad in jobs:
        build_one(src_name, out_name, pad)


if __name__ == "__main__":
    main()
