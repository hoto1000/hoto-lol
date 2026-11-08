"""Make share.png, the picture shown when a hoto.lol link is shared (Open Graph / social cards).

Run: python3 scripts/make_share_image.py   (needs Pillow; writes share.png at the repo root)
The image is committed, so the site build does not need Pillow. It uses the site's own
planet colors (site.css, dark theme) and Liberation Serif (SIL Open Font License).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, S = 1200, 630, 2          # draw at 2x, then shrink, for smooth curves
CANVAS, TEXT, MUTED = (5, 7, 13), (236, 239, 245), (166, 177, 198)
DAY, DUSK, TOP, LINE = (90, 169, 255), (255, 92, 99), (24, 42, 99), (43, 54, 84)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def main():
    img = Image.new("RGB", (W * S, H * S), CANVAS)
    d = ImageDraw.Draw(img)
    # Planet horizon: a large circle whose top rises from the bottom edge.
    r = 1500 * S
    cx, cy = W * S // 2, (H + 1500 - 190) * S
    box = (cx - r, cy - r, cx + r, cy + r)
    # soft fill fading from planet-top to canvas
    for i in range(0, 160 * S, 2):
        t = i / (160 * S)
        c = tuple(round(TOP[k] * (1 - t) + CANVAS[k] * t) for k in range(3))
        d.ellipse((box[0] + i, box[1] + i, box[2] - i, box[3] - i), outline=c, width=3)
    d.ellipse(box, fill=None, outline=LINE, width=2 * S)
    # rims: blue on the day (left) side, red on the dusk (right) side
    d.arc(box, 180 + 8, 270, fill=DAY, width=5 * S)
    d.arc(box, 270, 360 - 8, fill=DUSK, width=5 * S)
    # wordmark
    big = ImageFont.truetype(SERIF_BOLD, 112 * S)
    small = ImageFont.truetype(SERIF, 40 * S)
    a, b = "otohay ", "blog"
    wa = d.textlength(a, font=big)
    wb = d.textlength(b, font=big)
    x = (W * S - (wa + wb)) // 2
    y = 170 * S
    d.text((x, y), a, font=big, fill=TEXT)
    d.text((x + wa, y), b, font=big, fill=DUSK)
    sub = "hoto.lol"
    d.text(((W * S - d.textlength(sub, font=small)) // 2, y + 150 * S), sub, font=small, fill=MUTED)
    img.resize((W, H), Image.LANCZOS).save(ROOT / "share.png", optimize=True)


if __name__ == "__main__":
    main()
