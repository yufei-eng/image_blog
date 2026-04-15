"""PNG renderer for Photo Blog — screenshots the HTML output via headless browser.

Uses Playwright (Chromium) to take a full-page, 2x HiDPI screenshot of the
rendered HTML, producing a pixel-perfect long image identical to what the user
sees when opening the HTML in a browser.

Fallback: if Playwright is unavailable after auto-install attempt, renders a
dark-themed Pillow composite that visually matches the HTML style.
"""

import os
import subprocess
import sys


def _ensure_playwright() -> bool:
    """Try to make Playwright usable: install the package + Chromium if missing."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        pass

    print("  [INFO] Playwright not found, attempting auto-install...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "playwright"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120,
        )
    except Exception as e:
        print(f"  [WARN] pip install playwright failed: {e}")
        return False

    try:
        subprocess.check_call(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300,
        )
    except Exception as e:
        print(f"  [WARN] playwright install chromium failed: {e}")
        return False

    try:
        from playwright.sync_api import sync_playwright  # noqa: F811
        return True
    except ImportError:
        return False


def _screenshot_html(html_path: str, png_path: str, width: int = 1080, scale: int = 2) -> bool:
    """Take a full-page screenshot of an HTML file via Playwright. Returns True on success."""
    if not _ensure_playwright():
        return False

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": width, "height": 800},
                device_scale_factor=scale,
            )
            page.goto(f"file://{os.path.abspath(html_path)}")
            page.wait_for_timeout(1200)
            page.screenshot(path=png_path, full_page=True)
            browser.close()
        return os.path.exists(png_path)
    except Exception as e:
        print(f"  [WARN] Playwright screenshot failed: {e}")
        return False


def _fallback_composite(blog_content: dict, highlight_paths: list, png_path: str) -> str:
    """Dark-themed Pillow composite that visually matches the HTML output."""
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    SCALE = 2
    CANVAS_W = 1080 * SCALE
    PAD = 40 * SCALE
    INNER_PAD = 20 * SCALE

    BG = (10, 10, 15)
    TEXT_PRIMARY = (232, 232, 236)
    TEXT_SECONDARY = (184, 184, 196)
    TEXT_MUTED = (160, 160, 176)
    ACCENT = (91, 155, 213)
    CARD_BG = (20, 20, 28)
    DIVIDER = (255, 255, 255, 15)

    def _font(size):
        for fp in [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]:
            if os.path.exists(fp):
                try:
                    return ImageFont.truetype(fp, size * SCALE)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _wrap(draw, text, font, max_w):
        lines, cur = [], ""
        for ch in text:
            test = cur + ch
            if draw.textbbox((0, 0), test, font=font)[2] > max_w:
                if cur:
                    lines.append(cur)
                cur = ch
            else:
                cur = test
        if cur:
            lines.append(cur)
        return lines

    def _safe_open(path, max_w=None):
        try:
            img = ImageOps.exif_transpose(Image.open(path))
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            if max_w and img.width > max_w:
                ratio = max_w / img.width
                img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
            return img
        except Exception:
            return None

    title = blog_content.get("title", "Photo Blog")
    desc = blog_content.get("description", {})
    desc_text = desc.get("text", "") if isinstance(desc, dict) else str(desc)
    hero_idx = blog_content.get("hero_image_index", 0)
    insights = blog_content.get("insights", [])
    tip = blog_content.get("tip", "")
    footer_date = blog_content.get("footer_date", "")

    content_w = CANVAS_W - 2 * PAD
    title_font = _font(28)
    body_font = _font(15)
    section_font = _font(18)
    small_font = _font(12)

    est_height = 600 * SCALE + len(insights) * 200 * SCALE
    canvas = Image.new("RGB", (CANVAS_W, max(est_height, 3000 * SCALE)), BG)
    draw = ImageDraw.Draw(canvas)
    y = PAD

    hero_img = None
    if highlight_paths and hero_idx < len(highlight_paths):
        hero_img = _safe_open(highlight_paths[hero_idx], max_w=content_w)

    if hero_img:
        if hero_img.mode != "RGB":
            hero_img = hero_img.convert("RGB")
        ratio = content_w / hero_img.width
        hero_h = min(int(hero_img.height * ratio), int(400 * SCALE))
        hero_resized = hero_img.resize((content_w, hero_h), Image.LANCZOS)
        canvas.paste(hero_resized, (PAD, y))

        grad = Image.new("RGBA", (content_w, hero_h), (0, 0, 0, 0))
        grad_draw = ImageDraw.Draw(grad)
        for gy in range(hero_h):
            alpha = int(220 * (gy / hero_h) ** 1.5)
            grad_draw.line([(0, gy), (content_w, gy)], fill=(0, 0, 0, alpha))
        canvas.paste(Image.alpha_composite(
            hero_resized.convert("RGBA"),
            grad
        ).convert("RGB"), (PAD, y))

        title_y = y + hero_h - PAD - 10 * SCALE
        for tl in _wrap(draw, title, title_font, content_w - 2 * INNER_PAD):
            draw.text((PAD + INNER_PAD, title_y), tl, fill=(255, 255, 255), font=title_font)
            title_y += 35 * SCALE
        y += hero_h + INNER_PAD
    else:
        for tl in _wrap(draw, title, title_font, content_w):
            draw.text((PAD, y), tl, fill=(255, 255, 255), font=title_font)
            y += 35 * SCALE
        y += INNER_PAD

    if desc_text:
        for dl in _wrap(draw, desc_text, body_font, content_w - 8 * SCALE):
            draw.text((PAD + 4 * SCALE, y), dl, fill=TEXT_SECONDARY, font=body_font)
            y += 24 * SCALE
        y += 20 * SCALE

    draw.line([(PAD + 12 * SCALE, y), (PAD + 12 * SCALE, y + 22 * SCALE)], fill=ACCENT, width=3 * SCALE)
    draw.text((PAD + 24 * SCALE, y), "Insights", fill=(255, 255, 255), font=section_font)
    y += 36 * SCALE

    IMG_W = 140 * SCALE
    IMG_H = 105 * SCALE

    for i, ins in enumerate(insights):
        ins_text = ins.get("text", "")
        ins_idx = ins.get("image_index", 0)
        is_reverse = i % 2 == 1

        ins_img = None
        if ins_idx < len(highlight_paths):
            ins_img = _safe_open(highlight_paths[ins_idx], max_w=IMG_W)

        text_w = content_w - IMG_W - 14 * SCALE if ins_img else content_w
        wrapped = _wrap(draw, ins_text, body_font, text_w)
        block_h = max(len(wrapped) * 24 * SCALE, IMG_H) + 10 * SCALE

        while y + block_h > canvas.height - PAD:
            nc = Image.new("RGB", (CANVAS_W, canvas.height + 2000 * SCALE), BG)
            nc.paste(canvas, (0, 0))
            canvas = nc
            draw = ImageDraw.Draw(canvas)

        if ins_img:
            if ins_img.mode != "RGB":
                ins_img = ins_img.convert("RGB")
            thumb = ImageOps.fit(ins_img, (IMG_W, IMG_H), Image.LANCZOS)
            if is_reverse:
                img_x = PAD
                text_x = PAD + IMG_W + 14 * SCALE
            else:
                text_x = PAD
                img_x = PAD + content_w - IMG_W
            canvas.paste(thumb, (img_x, y))
        else:
            text_x = PAD

        text_y = y + 4 * SCALE
        for ln in wrapped:
            draw.text((text_x, text_y), ln, fill=TEXT_MUTED, font=body_font)
            text_y += 24 * SCALE

        y += block_h + 10 * SCALE

    if tip:
        y += 10 * SCALE
        tip_rect_h = 0
        tip_lines = _wrap(draw, tip, body_font, content_w - 36 * SCALE)
        tip_rect_h = (len(tip_lines) + 1) * 24 * SCALE + 24 * SCALE

        while y + tip_rect_h > canvas.height - PAD:
            nc = Image.new("RGB", (CANVAS_W, canvas.height + 1000 * SCALE), BG)
            nc.paste(canvas, (0, 0))
            canvas = nc
            draw = ImageDraw.Draw(canvas)

        tip_bg = (int(91 * 0.08 + 10), int(155 * 0.08 + 10), int(213 * 0.08 + 15))
        draw.rounded_rectangle(
            [(PAD, y), (PAD + content_w, y + tip_rect_h)],
            radius=12 * SCALE, fill=tip_bg,
        )
        draw.text((PAD + 18 * SCALE, y + 10 * SCALE), "Tips", fill=ACCENT, font=section_font)
        tip_y = y + 10 * SCALE + 28 * SCALE
        for tl in tip_lines:
            draw.text((PAD + 18 * SCALE, tip_y), tl, fill=TEXT_MUTED, font=body_font)
            tip_y += 24 * SCALE
        y += tip_rect_h + 16 * SCALE

    y += 16 * SCALE
    draw.line([(PAD, y), (PAD + content_w, y)], fill=(255, 255, 255, 15), width=1)
    y += 10 * SCALE
    draw.text((PAD, y), "Fleeting Thoughts", fill=ACCENT, font=small_font)
    if footer_date:
        date_w = draw.textbbox((0, 0), footer_date, font=small_font)[2]
        draw.text((PAD + content_w - date_w, y), footer_date, fill=(102, 102, 102), font=small_font)
    y += 24 * SCALE

    canvas = canvas.crop((0, 0, CANVAS_W, y + PAD))
    os.makedirs(os.path.dirname(png_path) or ".", exist_ok=True)
    canvas.save(png_path, "PNG")
    return png_path


def render_blog_png(blog_content: dict, highlight_paths: list, output_path: str, html_path: str = None) -> str:
    """Render blog as PNG. Uses HTML screenshot if available, otherwise dark-themed Pillow fallback."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if html_path and os.path.exists(html_path):
        if _screenshot_html(html_path, output_path):
            return output_path
        print("  [INFO] Falling back to dark-themed Pillow composite")

    _fallback_composite(blog_content, highlight_paths, output_path)
    return output_path
