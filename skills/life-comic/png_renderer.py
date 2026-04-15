"""PNG renderer for Life Comic — screenshots the HTML output via headless browser.

Uses Playwright (Chromium) to take a full-page, 2x HiDPI screenshot of the
rendered HTML, producing a pixel-perfect long image identical to what the user
sees when opening the HTML in a browser.

Fallback: if Playwright is unavailable after auto-install attempt, renders a
dark-themed Pillow composite that visually matches the HTML style.
"""

import os
import subprocess
import sys
from typing import Optional


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


def _fallback_composite(storyboard: dict, comic_image_path: Optional[str], png_path: str) -> str:
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
    ACCENT = (140, 90, 160)

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

    narrative = storyboard.get("narrative", {})
    title = narrative.get("title", storyboard.get("theme", "Life Comic"))
    body = narrative.get("body", "")
    content_w = CANVAS_W - 2 * PAD

    title_font = _font(28)
    body_font = _font(15)
    small_font = _font(12)

    canvas = Image.new("RGB", (CANVAS_W, 5000 * SCALE), BG)
    draw = ImageDraw.Draw(canvas)
    y = PAD

    for tl in _wrap(draw, title, title_font, content_w):
        draw.text((PAD, y), tl, fill=ACCENT, font=title_font)
        y += 35 * SCALE
    y += INNER_PAD

    if comic_image_path and os.path.exists(comic_image_path):
        try:
            ci = ImageOps.exif_transpose(Image.open(comic_image_path))
            if ci.mode != "RGB":
                ci = ci.convert("RGB")
            ratio = content_w / ci.width
            ch = int(ci.height * ratio)
            ci = ci.resize((content_w, ch), Image.LANCZOS)
            canvas.paste(ci, (PAD, y))
            y += ch + INNER_PAD
        except Exception:
            pass

    if body:
        for ln in _wrap(draw, body, body_font, content_w):
            while y + 24 * SCALE > canvas.height - PAD:
                nc = Image.new("RGB", (CANVAS_W, canvas.height + 2000 * SCALE), BG)
                nc.paste(canvas, (0, 0))
                canvas = nc
                draw = ImageDraw.Draw(canvas)
            draw.text((PAD, y), ln, fill=TEXT_SECONDARY, font=body_font)
            y += 24 * SCALE
        y += INNER_PAD

    y += 10 * SCALE
    draw.line([(PAD, y), (PAD + content_w, y)], fill=(255, 255, 255, 15), width=1)
    y += 10 * SCALE
    draw.text((PAD, y), "Life Comic", fill=ACCENT, font=small_font)
    y += 24 * SCALE

    canvas = canvas.crop((0, 0, CANVAS_W, y + PAD))
    os.makedirs(os.path.dirname(png_path) or ".", exist_ok=True)
    canvas.save(png_path, "PNG")
    return png_path


def render_comic_png(
    storyboard: dict,
    comic_image_path: Optional[str],
    reference_paths: list,
    output_path: str,
    html_path: str = None,
) -> str:
    """Render comic as PNG. Uses HTML screenshot if available, otherwise dark-themed Pillow fallback."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if html_path and os.path.exists(html_path):
        if _screenshot_html(html_path, output_path):
            return output_path
        print("  [INFO] Falling back to dark-themed Pillow composite")

    _fallback_composite(storyboard, comic_image_path, output_path)
    return output_path
