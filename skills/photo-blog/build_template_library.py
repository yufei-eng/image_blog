#!/usr/bin/env python3
"""One-time script: analyze 89 reference cover images with Gemini Pro.

Extracts structured style metadata from each reference image and saves
the result as template_library.json for use by cover_generator.py.

Usage:
    python3 build_template_library.py /path/to/reference/images/
    python3 build_template_library.py /path/to/reference/images/ --resume
"""

import argparse
import json
import math
import os
import sys
import time
from typing import Tuple

from google import genai
from google.genai import types

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "template_library.json")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

ANALYSIS_PROMPT = """Analyze this cover/poster template image and extract structured metadata.
This is a reference template from a photo collage app (like Meitu). I need you to describe
its visual style so I can reproduce a similar style for different content.

Return ONLY a valid JSON object with these fields:

{
  "style_category": "<one of: kawaii_cartoon, grunge_torn_paper, minimalist_magazine, dense_mosaic, japanese_traditional, pixel_y2k, sports_poster, travel_journal, monochrome_artistic, pastel_stamp, comic_panel, clean_grid, retro_film, watercolor_soft, bold_pop, neon_dark, botanical_natural, geometric_modern>",
  "mood": ["<3-5 mood tags from: playful, youthful, fun, warm, cozy, elegant, edgy, cool, energetic, serene, nostalgic, romantic, adventurous, artistic, minimalist, bold, dreamy, cheerful, sophisticated, whimsical>"],
  "color_palette": ["<3-5 dominant colors, e.g. pink, kraft_brown, navy, white, cyan, gold, coral, mint, charcoal, lavender, sage_green, cream, burgundy, teal, sunset_orange>"],
  "color_temperature": "<warm / cool / neutral>",
  "photo_count_range": [<min photos this layout works for>, <max photos>],
  "layout_type": "<one of: scattered_polaroid, structured_grid, asymmetric_magazine, dense_collage, single_hero, comic_panels, diagonal_dynamic, circular_frames, filmstrip, freeform_overlap>",
  "typography_style": "<one of: handwritten_script, bold_sans, elegant_serif, ransom_cutout, brush_stroke, pixel_font, mixed_playful, clean_modern, calligraphy, stamp_text>",
  "decoration_level": "<minimal / moderate / heavy>",
  "background_type": "<one of: solid_color, gradient, textured_paper, photo_bleed, pattern, transparent_overlay, dark_solid, watercolor_wash>",
  "theme_affinity": ["<3-6 themes from: food, travel, nature, urban, family, friends, romance, fashion, sports, culture, daily_life, celebration, seasons, pets, art, music, school, fitness>"],
  "visual_description": "<2-3 sentence description of the overall visual style, layout, and key design elements that make this template distinctive>"
}

IMPORTANT:
- Be precise and specific in the visual_description — it will be used as a prompt for image generation.
- photo_count_range should reflect how many photo slots the template has (e.g. [1,1] for single-photo, [6,9] for dense grid).
- Choose style_category carefully — each template should map to one clear category.
- Return ONLY the JSON, no markdown fences, no explanation."""


def _load_config() -> dict:
    config_path = os.path.join(SCRIPT_DIR, "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def _get_client(cfg: dict):
    api_cfg = cfg.get("compass_api", {})
    token = (os.environ.get("COMPASS_CLIENT_TOKEN")
             or os.environ.get("COMPASS_API_KEY")
             or os.environ.get("ANTHROPIC_API_KEY")
             or os.environ.get("GOOGLE_API_KEY")
             or os.environ.get("GEMINI_API_KEY")
             or api_cfg.get("client_token", ""))
    base_url = (os.environ.get("COMPASS_BASE_URL")
                or os.environ.get("ANTHROPIC_BASE_URL")
                or api_cfg.get("base_url", ""))
    http_opts = types.HttpOptions(base_url=base_url) if base_url else None
    return genai.Client(api_key=token, http_options=http_opts)


def _load_image_bytes(path: str, max_pixels: int = 1200 * 1200) -> Tuple[bytes, str]:
    try:
        from PIL import Image, ImageOps
        import io
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        w, h = img.size
        if w * h > max_pixels:
            ratio = math.sqrt(max_pixels / (w * h))
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        with open(path, "rb") as f:
            return f.read(), "image/png"


def analyze_single_image(client, model: str, image_path: str) -> dict:
    img_data, mime = _load_image_bytes(image_path)

    parts = [
        types.Part.from_bytes(data=img_data, mime_type=mime),
        types.Part.from_text(text=ANALYSIS_PROMPT),
    ]

    response = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=parts)],
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description="Build template library from reference images")
    parser.add_argument("image_dir", help="Directory containing reference cover images")
    parser.add_argument("--resume", action="store_true", help="Resume from existing partial results")
    parser.add_argument("--batch-size", type=int, default=5, help="Pause between batches")
    args = parser.parse_args()

    cfg = _load_config()
    client = _get_client(cfg)
    model = cfg.get("compass_api", {}).get("understanding_model", "gemini-3-pro-preview")

    image_files = sorted([
        f for f in os.listdir(args.image_dir)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTS
    ])
    print(f"Found {len(image_files)} reference images in {args.image_dir}")

    existing = {}
    if args.resume and os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH) as f:
            existing_list = json.load(f)
        existing = {t["file"]: t for t in existing_list}
        print(f"Resuming: {len(existing)} already analyzed")

    results = list(existing.values())
    pending = [f for f in image_files if f not in existing]
    print(f"Pending: {len(pending)} images to analyze")

    for i, filename in enumerate(pending):
        filepath = os.path.join(args.image_dir, filename)
        ref_id = f"ref_{os.path.splitext(filename)[0].split('_')[-2]}"

        print(f"\n[{i+1}/{len(pending)}] Analyzing {filename} (id={ref_id})...")

        try:
            metadata = analyze_single_image(client, model, filepath)
            metadata["id"] = ref_id
            metadata["file"] = filename
            results.append(metadata)
            print(f"  Style: {metadata.get('style_category', '?')}, "
                  f"Mood: {metadata.get('mood', [])[:3]}, "
                  f"Photos: {metadata.get('photo_count_range', '?')}")
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "id": ref_id,
                "file": filename,
                "error": str(e),
                "style_category": "unknown",
                "mood": [],
                "color_palette": [],
                "color_temperature": "neutral",
                "photo_count_range": [1, 9],
                "layout_type": "freeform_overlap",
                "typography_style": "mixed_playful",
                "decoration_level": "moderate",
                "background_type": "solid_color",
                "theme_affinity": ["daily_life"],
                "visual_description": "Analysis failed, using fallback.",
            })

        if (i + 1) % args.batch_size == 0:
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"  [CHECKPOINT] Saved {len(results)} templates to {OUTPUT_PATH}")
            time.sleep(1)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    categories = {}
    for t in results:
        cat = t.get("style_category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\n{'='*60}")
    print(f"  TEMPLATE LIBRARY BUILT — {len(results)} templates")
    print(f"  Saved to: {OUTPUT_PATH}")
    print(f"\n  Style distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
