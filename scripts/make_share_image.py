"""Make share.png, the picture shown when a hoto.lol link is shared (Open Graph / social cards).

Run: python3 scripts/make_share_image.py   (needs Pillow; writes share.png at the repo root)
The image is committed, so the site build does not need Pillow. Black and white to match the
site and Nick's hand-drawn ink logo (scripts/assets/hoto-logo-512.png): white paper, black ink,
the logo on the left and the wordmark on the right. Liberation Serif (SIL Open Font License).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, S = 1200, 630, 2          # draw at 2x, then shrink, for smooth edges
PAPER, INK, MUTED, LINE = (255, 255, 255), (17, 17, 17), (85, 85, 85), (212, 212, 212)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
LOGO = ROOT / "scripts" / "assets" / "hoto-logo-512.png"


def main():
    img = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)
    # A thin ink frame, like a printed card.
    m = 36 * S
    d.rectangle((m, m, W * S - m, H * S - m), outline=INK, width=3 * S)
    # The logo in a ring on the left.
    size = 360 * S
    lx, ly = 120 * S, (H * S - size) // 2
    logo = Image.open(LOGO).convert("RGBA").resize((size, size), Image.LANCZOS)
    img.paste(logo, (lx, ly), logo)
    d.ellipse((lx - 6 * S, ly - 6 * S, lx + size + 6 * S, ly + size + 6 * S), outline=INK, width=4 * S)
    # Wordmark and address on the right.
    big = ImageFont.truetype(SERIF_BOLD, 104 * S)
    small = ImageFont.truetype(SERIF, 40 * S)
    tx = lx + size + 70 * S
    d.text((tx, 200 * S), "otohay", font=big, fill=INK)
    d.text((tx, 310 * S), "blog", font=big, fill=INK)
    d.line((tx, 448 * S, tx + 90 * S, 448 * S), fill=INK, width=4 * S)
    d.text((tx, 470 * S), "hoto.lol", font=small, fill=MUTED)
    img.resize((W, H), Image.LANCZOS).save(ROOT / "share.png", optimize=True)


if __name__ == "__main__":
    main()
