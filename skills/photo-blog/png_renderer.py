"""PNG composite renderer for Photo Blog.

Creates a single shareable PNG image combining title, photos, and text.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

CANVAS_W = 1080
CARD_PADDING = 40
PHOTO_SPACING = 16
BG_COLOR = (255, 252, 248)
TEXT_COLOR = (50, 50, 50)
ACCENT_COLOR = (180, 120, 70)


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


def _fit_photo(path: str, target_w: int, target_h: int) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = ImageOps.fit(img, (target_w, target_h), Image.LANCZOS)
    return img


def _wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = list(text)
    lines, cur = [], ""
    for ch in words:
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


def render_blog_png(blog_content: dict, highlight_paths: list[str], output_path: str) -> str:
    """Render blog as a single composite PNG."""
    title = blog_content.get("title", "Photo Blog")
    desc = blog_content.get("description", {}).get("text", "")
    insights = blog_content.get("insights", [])
    footer_date = blog_content.get("footer_date", "")

    title_font = _load_font(48)
    body_font = _load_font(24)
    small_font = _load_font(18)

    content_w = CANVAS_W - 2 * CARD_PADDING
    n_photos = len(highlight_paths)

    if n_photos <= 1:
        cols = 1
    elif n_photos <= 4:
        cols = 2
    else:
        cols = 3

    photo_w = (content_w - (cols - 1) * PHOTO_SPACING) // cols
    photo_h = int(photo_w * 0.75)
    rows = (n_photos + cols - 1) // cols
    photos_block_h = rows * photo_h + (rows - 1) * PHOTO_SPACING

    estimated_h = (
        CARD_PADDING + 80
        + 60
        + photos_block_h
        + 40
        + len(insights) * 70
        + 80
        + CARD_PADDING
    )

    canvas = Image.new("RGB", (CANVAS_W, max(estimated_h, 600)), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    y = CARD_PADDING

    draw.line([(CARD_PADDING, y + 60), (CANVAS_W - CARD_PADDING, y + 60)], fill=ACCENT_COLOR, width=2)
    title_lines = _wrap_text(draw, title, title_font, content_w)
    for tl in title_lines:
        draw.text((CARD_PADDING, y), tl, fill=ACCENT_COLOR, font=title_font)
        y += 55
    y += 20

    if desc:
        desc_lines = _wrap_text(draw, desc, body_font, content_w)
        for dl in desc_lines:
            draw.text((CARD_PADDING, y), dl, fill=TEXT_COLOR, font=body_font)
            y += 30
        y += 20

    for idx, path in enumerate(highlight_paths):
        row, col = divmod(idx, cols)
        px = CARD_PADDING + col * (photo_w + PHOTO_SPACING)
        py = y + row * (photo_h + PHOTO_SPACING)
        try:
            photo = _fit_photo(path, photo_w, photo_h)
            canvas.paste(photo, (px, py))
        except Exception:
            draw.rectangle([(px, py), (px + photo_w, py + photo_h)], fill=(220, 220, 220))

    y += photos_block_h + 30

    for i, ins in enumerate(insights):
        text = ins.get("text", "")
        lines = _wrap_text(draw, f"{i+1}. {text}", body_font, content_w)
        for ln in lines:
            if y + 30 > canvas.height - CARD_PADDING:
                new_canvas = Image.new("RGB", (CANVAS_W, canvas.height + 600), BG_COLOR)
                new_canvas.paste(canvas, (0, 0))
                canvas = new_canvas
                draw = ImageDraw.Draw(canvas)
            draw.text((CARD_PADDING, y), ln, fill=TEXT_COLOR, font=body_font)
            y += 30
        y += 10

    if footer_date:
        y += 20
        draw.text((CARD_PADDING, y), footer_date, fill=(150, 150, 150), font=small_font)
        y += 40

    canvas = canvas.crop((0, 0, CANVAS_W, min(y + CARD_PADDING, canvas.height)))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    canvas.save(output_path, "PNG")
    return output_path
