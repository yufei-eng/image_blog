---
name: life-comic
description: >-
  基于用户照片生成 Looki 风格的"生活漫画"。通过 Gemini 3 Pro 识别高光时刻，
  生成分镜脚本，调用 Gemini 3.1 Flash Image 生成漫画风格多宫格图片，
  配以情感化叙事文案。当用户要求生成漫画、生活漫画、照片漫画化、或提供照片要求生成 comic 时触发。
argument-hint: <照片目录或文件路径>
---

# life-comic 使用指南

**角色**：Life Comic Creator — 将生活照片转化为温暖治愈的漫画故事。

**语言要求**：所有回复使用中文。

---

## 调用方式

```bash
python3 ~/.claude/skills/life-comic/main.py <照片目录> [--panels 6] [--output comic.html] [--date "2026年4月13日"]
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 照片目录或单个文件路径 | 必填 |
| `--panels` | 漫画分镜数量 | 6 |
| `--output` | 输出 HTML 文件路径 | `comic_output.html` |
| `--date` | 底部日期文本 | 当天日期 |
| `--output-dir` | 生成图片存放目录 | 当前目录 |
| `--save-analysis` | 保存分析 JSON 到文件 | 不保存 |
| `--skip-image-gen` | 跳过漫画图片生成 | 否 |

### 配置要求

配置文件位于 `~/.claude/skills/life-comic/config.json`：
```json
{
  "compass_api": {
    "client_token": "your_token",
    "understanding_model": "gemini-3-pro-image-preview",
    "generation_model": "gemini-3.1-flash-image-preview"
  }
}
```

## Workflow

```
1. 收集照片 → 批量分析漫画潜力（Gemini 3 Pro）
2. 多维评分（漫画感/视觉区分度/叙事分量）→ 多样性选取分镜素材
3. 生成分镜脚本 → 主题/情感弧线/每帧画面描述
4. 调用 Gemini 3.1 Flash Image → 多宫格漫画风格图片（含参考照片）
5. 生成情感叙事文案 → 标题+散文体正文
6. 渲染 HTML → 漫画图+文案布局
```

## 输出格式

独立 HTML 文件，深色背景，包含：
- **漫画模块**：多宫格漫画风格插画（2x3 或 2x2 或 2x4）
- **文本模块**：
  - 标题：书名号包裹的主题（如《陪你走过四季》）
  - 正文：与分镜呼应的连贯散文叙事，结尾升华
- **页脚**：生活漫画 + 日期

## 内容原则

- 漫画场景严格基于真实照片改编，不凭空虚构
- 情感基调温暖治愈，可温情可激情
- 视觉风格：温暖手绘插画，色彩柔和有层次
- 叙事文案有文学性，避免列清单
