---
name: life-comic
description: >-
  Generate Looki-style "Life Comics" from user photos. Uses Gemini 3 Pro to identify
  highlight moments, generates a storyboard script, calls Gemini 3.1 Flash Image
  to create multi-panel comic-style illustrations, and pairs them with emotional narrative.
  Triggered when the user asks to generate a comic, life comic, photo-to-comic, or
  provides photos to create a comic.
argument-hint: <photo directory or file path>
---

# life-comic Usage Guide

**Role**: Life Comic Creator — transform everyday photos into warm, heartfelt comic stories.

---

## Usage

```bash
python3 ~/.claude/skills/life-comic/main.py <photo_dir> [--panels 6] [--output comic.html] [--date "2026-04-13"]
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `input` | Photo directory or single file path | Required |
| `--panels` | Number of comic panels | 6 |
| `--output` | Output HTML file path | `comic_output.html` |
| `--date` | Footer date text (auto-detected from EXIF/filename if omitted) | Auto |
| `--output-dir` | Directory for generated images | Current dir |
| `--save-analysis` | Save analysis JSON to file | None |
| `--skip-image-gen` | Skip comic image generation | No |

### Configuration

Config file at `~/.claude/skills/life-comic/config.json`:
```json
{
  "compass_api": {
    "client_token": "your_token",
    "understanding_model": "gemini-3-pro-preview",
    "generation_model": "gemini-3.1-flash-image-preview"
  }
}
```

## Workflow

```
1. Collect photos → Batch analyze comic potential (Gemini 3 Pro)
2. Multi-dimensional scoring (comic appeal / visual distinctness / narrative weight) → Diversity-optimized panel selection
3. Generate storyboard script → Theme / emotional arc / per-panel scene descriptions
4. Call Gemini 3.1 Flash Image → Multi-panel comic-style illustration (with reference photos)
5. Generate emotional narrative → Title + prose body
6. Render HTML → Comic image + narrative layout
```

## Output Format

Self-contained HTML file with dark background:
- **Comic Module**: Multi-panel comic-style illustration (2x3 / 2x2 / 2x4 grid)
- **Text Module**:
  - Title: Thematic title
  - Body: Cohesive prose narrative corresponding to comic panels, with uplifting conclusion
- **Footer**: "Life Comic" + date

## Content Principles

- Comic scenes strictly adapted from real photos — never fabricate
- Warm, heartfelt emotional tone
- Visual style: warm hand-drawn illustration, soft layered colors
- Narrative has literary quality — avoid list-style writing
