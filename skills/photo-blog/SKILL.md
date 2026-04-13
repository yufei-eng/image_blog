---
name: photo-blog
description: >-
  Generate Looki-style "Photo Blog" posts from user photos. Uses Gemini 3 Pro to understand
  photo content, intelligently selects highlight images, and generates a visual blog with
  title, description, insights (photo+text pairs), and tips.
  Triggered when the user asks to generate a photo blog, photo diary, visual recap,
  or provides a photo directory to create a blog.
argument-hint: <photo directory or file path>
---

# photo-blog Usage Guide

**Role**: Photo Blog Creator — turn photos into evocative visual stories.

---

## Usage

```bash
python3 ~/.claude/skills/photo-blog/main.py <photo_dir> [--max-highlights 8] [--output blog.html] [--date "2026-04-13"]
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `input` | Photo directory or single file path | Required |
| `--max-highlights` | Max number of highlight photos to select | 8 |
| `--output` | Output HTML file path | `blog_output.html` |
| `--date` | Footer date text (auto-detected from EXIF/filename if omitted) | Auto |
| `--save-analysis` | Save analysis JSON to file | None |

### Configuration

Uses Compass API. Config file at `~/.claude/skills/photo-blog/config.json`:
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
1. Collect photos → Batch analyze (Gemini 3 Pro, 5 per batch)
2. Multi-dimensional scoring (visual/story/emotion/uniqueness/technical) → Diversity-optimized highlight selection
3. Generate narrative (title / description / insights / tips) → Warm, evocative style
4. Render HTML → Dark-themed card layout with embedded base64 images
```

## Output Format

Self-contained HTML file with dark background card layout:
- **Title**: Poetic and concise (e.g., "Afternoon Among the Peaks")
- **Description**: Hero image + 2-4 sentence coherent narrative
- **Insights**: Up to 8 photo+text pairs, alternating layout
- **Tips**: Personalized practical advice based on scene context
- **Footer**: "Fleeting Thoughts" + date

## Content Principles

- Strictly based on real photo content — never fabricate scenes or events
- Warm, evocative writing style that emphasizes emotional resonance
- Each insight has a different focus — no repetitive descriptions
