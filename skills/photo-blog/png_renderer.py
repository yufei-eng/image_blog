"""PNG renderer for Photo Blog — screenshots the HTML output via headless browser.

Uses Playwright (Chromium) to take a full-page, 2x HiDPI screenshot of the
rendered HTML, producing a pixel-perfect long image identical to what the user
sees when opening the HTML in a browser.

If Playwright is unavailable, PNG generation is skipped entirely — the caller
should provide HTML and rich-text outputs instead.
"""

import os
import subprocess
import sys


def _ensure_playwright() -> bool:
    """Ensure the Playwright Python package is importable."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
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
        from playwright.sync_api import sync_playwright  # noqa: F811, F401
        return True
    except ImportError:
        return False


def _install_chromium() -> bool:
    """Install Chromium browser binary for Playwright."""
    print("  [INFO] Chromium browser not found, installing...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            timeout=300,
        )
        return True
    except Exception as e:
        print(f"  [WARN] playwright install chromium failed: {e}")
        return False


def _screenshot_html(html_path: str, png_path: str, width: int = 480, scale: int = 2) -> bool:
    """Take a full-page screenshot of an HTML file via Playwright. Returns True on success."""
    if not _ensure_playwright():
        return False

    from playwright.sync_api import sync_playwright

    for attempt in range(2):
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
            if attempt == 0 and "Executable doesn't exist" in str(e):
                if _install_chromium():
                    continue
            print(f"  [WARN] Playwright screenshot failed: {e}")
            return False
    return False


def render_blog_png(blog_content: dict, highlight_paths: list, output_path: str, html_path: str = None) -> str | None:
    """Render blog as PNG via HTML screenshot. Returns path on success, None on failure."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if html_path and os.path.exists(html_path):
        if _screenshot_html(html_path, output_path):
            return output_path

    print("  [SKIP] PNG generation skipped — Playwright unavailable. Use HTML or rich-text output.")
    return None
