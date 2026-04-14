"""PNG composite renderer for Life Comic.

Creates a single shareable PNG image combining the generated comic, narrative, and metadata.
"""

import os
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps

CANVAS_W = 1080
CARD_PADDING = 40
BG_COLOR = (255, 252, 248)
TEXT_COLOR = (50, 50, 50)
ACCENT_COLOR = (140, 90, 160)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) > max_w:
            if cur:
                lines.append(cur)
            cur = ch
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def render_comic_png(
    storyboard: dict,
    comic_image_path: Optional[str],
    reference_paths: list[str],
    output_path: str,
) -> str:
    """Render comic as a single composite PNG. Returns output path."""
    theme = storyboard.get("theme", "Life Comic")
    narrative = storyboard.get("narrative", {})
    title = narrative.get("title", theme)
    body = narrative.get("body", "")
    footer_date = storyboard.get("footer_date", "")

    title_font = _load_font(48)
    body_font = _load_font(22)
    small_font = _load_font(18)
    content_w = CANVAS_W - 2 * CARD_PADDING

    comic_img = None
    comic_h = 0
    if comic_image_path and os.path.exists(comic_image_path):
        comic_img = Image.open(comic_image_path)
        comic_img = ImageOps.exif_transpose(comic_img)
        if comic_img.mode != "RGB":
            comic_img = comic_img.convert("RGB")
        ratio = content_w / comic_img.width
        comic_h = int(comic_img.height * ratio)
        comic_img = comic_img.resize((content_w, comic_h), Image.LANCZOS)

    estimated_h = CARD_PADDING + 80 + comic_h + 40 + 400 + CARD_PADDING
    canvas = Image.new("RGB", (CANVAS_W, max(estimated_h, 600)), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    y = CARD_PADDING

    for tl in _wrap_text(draw, title, title_font, content_w):
        draw.text((CARD_PADDING, y), tl, fill=ACCENT_COLOR, font=title_font)
        y += 55
    y += 10

    draw.text((CARD_PADDING, y), theme, fill=(120, 120, 120), font=small_font)
    y += 30

    if comic_img:
        canvas.paste(comic_img, (CARD_PADDING, y))
        y += comic_h + 20

    draw.line([(CARD_PADDING, y), (CANVAS_W - CARD_PADDING, y)], fill=ACCENT_COLOR, width=2)
    y += 20

    if body:
        for ln in _wrap_text(draw, body, body_font, content_w):
            if y + 30 > canvas.height - CARD_PADDING:
                new_canvas = Image.new("RGB", (CANVAS_W, canvas.height + 600), BG_COLOR)
                new_canvas.paste(canvas, (0, 0))
                canvas = new_canvas
                draw = ImageDraw.Draw(canvas)
            draw.text((CARD_PADDING, y), ln, fill=TEXT_COLOR, font=body_font)
            y += 28
        y += 20

    if footer_date:
        draw.text((CARD_PADDING, y), footer_date, fill=(150, 150, 150), font=small_font)
        y += 40

    canvas = canvas.crop((0, 0, CANVAS_W, min(y + CARD_PADDING, canvas.height)))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    canvas.save(output_path, "PNG")
    return output_path
