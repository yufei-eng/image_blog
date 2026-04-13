# Looki-style Photo Blog & Life Comic Skills

Claude Code Skills powered by Gemini 3 Pro (image understanding) + Gemini 3.1 Flash Image (comic generation), replicating the core content generation features of the Looki App.

## Two Skills

### photo-blog — Photo Blog Generator

Transform photos into evocative visual stories with poetic titles, scene descriptions, photo insights, and personalized tips.

```bash
python3 skills/photo-blog/main.py <photo_dir> --max-highlights 8 --output blog.html
```

### life-comic — Life Comic Generator

Transform photos into warm, heartfelt multi-panel comics with emotional prose narrative.

```bash
python3 skills/life-comic/main.py <photo_dir> --panels 6 --output comic.html
```

## Technical Architecture

```
Photo input → Gemini 3 Pro batch understanding → Multi-dimensional scoring + Diversity selection
                                                        ↓
                                           photo-blog: Narrative generation → HTML rendering
                                           life-comic: Storyboard script → Gemini 3.1 Flash Image comic gen → HTML rendering
```

**Key features**:
- Multi-dimensional scoring system (visual/story/emotion/uniqueness/technical) inspired by ai-instagram-organizer
- Greedy diversity selection algorithm to avoid repetitive scenes
- Comic generation leverages Gemini 3.1 Flash Image's multi-reference capability (up to 14 images)
- EXIF orientation auto-fix (ImageOps.exif_transpose) across all image loading paths
- Photo date auto-extraction from EXIF metadata or filename
- All content strictly grounded in real photo content — no fabrication

## Configuration

```bash
cp skills/photo-blog/config.json.example skills/photo-blog/config.json
# Edit config.json and fill in your Compass API client_token
```

## Dependencies

```bash
pip install google-genai Pillow
```

## Test Results

Tested on 98 travel photos across 10 cases (5 Blog + 5 Comic):

| Skill | Avg Score | Example Titles |
|-------|-----------|----------------|
| Photo Blog | 8.0/10 | Various unique poetic titles per case |
| Life Comic | 8.8/10 | Various unique creative titles per case |

See `report/project_report.html` for the full report.

## Project Structure

```
├── skills/
│   ├── photo-blog/         # Photo Blog Skill
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   ├── image_analyzer.py
│   │   ├── blog_generator.py
│   │   └── html_renderer.py
│   └── life-comic/         # Life Comic Skill
│       ├── SKILL.md
│       ├── main.py
│       ├── image_analyzer.py
│       ├── comic_generator.py
│       └── html_renderer.py
├── report/
│   ├── project_report.html # Comprehensive project report
│   ├── blog/               # Blog analysis JSONs
│   └── comic/              # Comic images + analysis JSONs
└── README.md
```
