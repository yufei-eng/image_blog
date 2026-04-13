# Looki-style 图文Blog & 生活漫画 Skill

基于 Gemini 3 Pro（图像理解）+ Gemini 3.1 Flash Image（漫画生成）的 Claude Code Skill，复刻 Looki App 的核心内容生成功能。

## 两个 Skill

### photo-blog — 图文 Blog 生成

将照片转化为有温度的图文故事，包含诗意标题、场景描述、照片洞察和个性化建议。

```bash
python3 skills/photo-blog/main.py <照片目录> --max-highlights 8 --output blog.html
```

### life-comic — 生活漫画生成

将照片转化为温暖治愈的多宫格漫画，配以情感化叙事文案。

```bash
python3 skills/life-comic/main.py <照片目录> --panels 6 --output comic.html
```

## 技术架构

```
照片输入 → Gemini 3 Pro 批量理解 → 多维评分 + 多样性选取
                                         ↓
                              photo-blog: 文案生成 → HTML渲染
                              life-comic: 分镜脚本 → Gemini 3.1 Flash Image 漫画生成 → HTML渲染
```

**核心特点**：
- 多维评分体系（视觉/叙事/情感/独特性/技术）借鉴 ai-instagram-organizer
- 多样性贪心选取算法，避免重复场景
- 漫画生成利用 Gemini 3.1 Flash Image 的多参考图能力（最多14张）
- 所有内容严格基于照片真实内容，不虚构

## 配置

```bash
cp skills/photo-blog/config.json.example skills/photo-blog/config.json
# 编辑 config.json，填入你的 Compass API client_token
```

## 安装依赖

```bash
pip install google-genai Pillow
```

## 测试结果

在 98 张成都旅行照片上测试了 10 个 case（5 Blog + 5 Comic）：

| 场景 | 平均评分 | 示例标题 |
|------|----------|----------|
| 图文Blog | 7.9/10 | 蜀地烟火记、一半烟火一半闲、雨夜烟火拾光 |
| 生活漫画 | 8.6/10 | 烟火漫游、沸腾烟火气、寻味慢时光 |

详细报告见 `report/project_report.html`。

## 项目结构

```
├── skills/
│   ├── photo-blog/         # 图文 Blog Skill
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   ├── image_analyzer.py
│   │   ├── blog_generator.py
│   │   └── html_renderer.py
│   └── life-comic/         # 生活漫画 Skill
│       ├── SKILL.md
│       ├── main.py
│       ├── image_analyzer.py
│       ├── comic_generator.py
│       └── html_renderer.py
├── report/
│   ├── project_report.html # 综合项目报告
│   ├── blog/               # Blog 分析 JSON
│   └── comic/              # 漫画图片 + 分析 JSON
└── README.md
```
