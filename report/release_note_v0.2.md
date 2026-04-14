# Image-blog 重磅发布v0.2  https://github.com/yufei-eng/image_blog

- 新增灵活图片数量支持（1~9张），单张极简模式到9张全景叙事自由切换，漫画宫格布局自适应（1x1/2x2/2x3/3x3等）
- 新增主题/风格关键词引导生成，通过 `--theme` 参数指定创作方向（如"美食之旅""城市夜景"），素材不匹配时自动回退并推荐3个候选主题
- 新增三格式输出：HTML（独立页面）、Rich Text（Markdown，兼容对话Agent）、PNG（合成分享图），通过 `--format` 一键切换或全部生成
- 优化用户意图识别，扩展触发词覆盖"生活总结""每日回顾""记忆拼图"等场景，生成后主动建议漫画/Blog互转和主题替换
- Rich Text 输出格式对齐 BeeAI 对话前端 Copilot Block 协议（`type: copilot, format: markdown`），支持标题/引用/分割线/图片引用

## 核心亮点

- 支持1~9张图片灵活输入，从单图故事到多图长卷全场景覆盖，评分与选取算法自动适配不同规模
- 主题引导 + 智能回退机制：用户指定主题时优先匹配，素材不足时降级为自动主题并返回候选建议，避免强行生成不相关内容
- 三格式并行输出，适配不同使用场景：IDE 开发调试用 HTML、对话 Agent 聊天窗口用 Rich Text、社交分享用 PNG 合成图
- 每次生成自动附带3个候选主题推荐（`suggested_themes`），帮助用户发现照片素材的更多创作角度
- 生成后交互优化：主动询问是否需要漫画版/Blog版互转、是否切换主题、是否换输出格式
- 98张测试照片 × 10个v0.2 case验证，覆盖1/2/3/4/5/6/9张等多种数量组合，三格式输出全部通过

## 使用方式
支持在 Claude Code 加载安装后使用
```bash
# 图文 Blog（指定主题 + 全格式输出）
python3 ~/.claude/skills/photo-blog/main.py <照片目录> --max-highlights 6 --theme "美食之旅" --format all --output blog.html

# 生活漫画（9宫格 + 主题引导）
python3 ~/.claude/skills/life-comic/main.py <照片目录> --panels 9 --theme "霓虹之梦" --format all --output comic.html

# 单张照片极简Blog
python3 ~/.claude/skills/photo-blog/main.py photo.jpg --max-highlights 1 --format richtext --output blog.html

# 对话Agent场景（输出Markdown富文本）
python3 ~/.claude/skills/life-comic/main.py <照片目录> --panels 4 --format richtext --output comic.html
```
