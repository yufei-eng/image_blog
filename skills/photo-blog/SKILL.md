---
name: photo-blog
description: >-
  基于用户照片生成 Looki 风格的"图文Blog"。通过 Gemini 3 Pro 理解照片内容，
  智能筛选高光素材，生成包含主标题、描述、洞察（照片+文案）、小建议的图文报告。
  当用户要求生成图文博客、照片日记、图文回顾、或提供照片目录要求生成 blog 时触发。
argument-hint: <照片目录或文件路径>
---

# photo-blog 使用指南

**角色**：Photo Blog Creator — 将照片转化为有温度的图文故事。

**语言要求**：所有回复使用中文。

---

## 调用方式

```bash
python3 ~/.claude/skills/photo-blog/main.py <照片目录> [--max-highlights 8] [--output blog.html] [--date "2026年4月13日"]
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 照片目录或单个文件路径 | 必填 |
| `--max-highlights` | 最多选取的高光照片数 | 8 |
| `--output` | 输出 HTML 文件路径 | `blog_output.html` |
| `--date` | 底部日期文本 | 当天日期 |
| `--save-analysis` | 保存分析 JSON 到文件 | 不保存 |

### 配置要求

使用 Compass API，配置文件位于 `~/.claude/skills/photo-blog/config.json`：
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
1. 收集照片 → 批量分析（Gemini 3 Pro，每批5张）
2. 多维评分（视觉/叙事/情感/独特性/技术）→ 多样性优化选取高光
3. 生成文案（标题/描述/洞察/建议）→ 感性温暖风格
4. 渲染 HTML → 深色卡片式布局，内嵌 base64 图片
```

## 输出格式

独立 HTML 文件，深色背景卡片式布局，包含：
- **主标题**：诗意凝练（如"峰林间午后"）
- **描述模块**：精选头图 + 60-100字连贯叙事
- **洞察模块**：最多8对（照片+文案），图文交替排列
- **小建议**：场景化的个性化实用建议
- **页脚**：片刻感悟 + 日期

## 内容原则

- 严格基于真实照片内容，绝不虚构场景或事件
- 文风感性温暖，强化情感共鸣
- 避免流水账式叙述，每段洞察各有侧重
