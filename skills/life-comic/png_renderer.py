"""PNG renderer for Life Comic — screenshots the HTML output via headless browser.

Uses Playwright (Chromium) to take a full-page, 2x HiDPI screenshot of the
rendered HTML, producing a pixel-perfect long image identical to what the user
sees when opening the HTML in a browser.

If Playwright is unavailable, PNG generation is skipped entirely — the caller
should provide HTML and rich-text outputs instead.
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


def render_comic_png(
    storyboard: dict,
    comic_image_path: Optional[str],
    reference_paths: list,
    output_path: str,
    html_path: str = None,
) -> str | None:
    """Render comic as PNG via HTML screenshot. Returns path on success, None on failure."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if html_path and os.path.exists(html_path):
        if _screenshot_html(html_path, output_path):
            return output_path

    print("  [SKIP] PNG generation skipped — Playwright unavailable. Use HTML or rich-text output.")
    return None
