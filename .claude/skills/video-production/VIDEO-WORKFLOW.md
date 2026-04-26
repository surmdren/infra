# YouTube 视频制作流程

DreamWise AI 频道完整制作流程，覆盖从选题到复盘的每一步。

---

## 流程总览

```
[可选] 竞品研究
    ↓
阶段一：前期准备
  1. youtube-creator-research  → 研究报告
  2. video-script-generator    → 脚本 + 制作包
  3. html-visual-generator     → 概念图 HTML（5-7张）
  4. seedream                  → 氛围图
  5. libtv-skill               → B-roll 动画
  6. video-checklist           → 制作 checklist
    ↓
阶段二：录制
  7. 屏幕录制（Demo 段）
  8. 真人出镜（口播段）
    ↓
阶段三：剪辑
  9. 剪映 / CapCut（手动）
    ↓
阶段四：发布
  10. youtube-description-generator → 说明 + 时间戳
  11. html-visual-generator          → YouTube 封面
  12. youtube-uploader               → 上传视频
  13. linkedin-post-generator        → LinkedIn 配图 + 发帖
    ↓
阶段五：复盘
  14. video-retrospective            → 改进点 → style-guide.md
```

---

## 各 Skill 详细说明

### 0. youtube-creator-research（可选）
**触发时机：** 新选题前，研究同行做法

| | 说明 |
|---|---|
| **输入** | 行业关键词（如 "Claude Code tutorial"）或博主频道 URL |
| **输出** | 研究报告：选题规律、标题公式、内容框架、制作工具清单 |
| **保存位置** | `creator-notes/[年月]/[期数]/research.md` |
| **用法** | `/youtube-creator-research Claude Code AI agents` |

---

### 1. video-script-generator
**触发时机：** 确定选题后，开始写脚本

| | 说明 |
|---|---|
| **输入** | 视频主题（必填）、目标受众、时长目标、风格参考、研究报告路径 |
| **输出** | 完整制作包（`.md` 文件）：10个候选标题、Part 1-5 脚本、素材分配表、封面文案、YouTube 描述模板、Tags、素材待办清单 |
| **保存位置** | `creator-notes/[年月]/[期数]/[slug]-production-pack.md` |
| **用法** | `/video-script-generator Claude Code Multi-Agent 用法，8-12分钟` |
| **依赖** | 自动读取 `video-production/oral-style-guide.md` |

**制作包结构：**
```
Part 1 — 完整口播脚本（带时间码）
Part 2 — 提词器版（短句 + 停顿标记）
Part 3 — 画面与制作笔记（镜头 + B-roll + 字幕）
Part 4 — 节奏与停顿设计
Part 5 — 一体版（拍摄专用，Part 1-4 合并）
```

---

### 2. html-visual-generator
**触发时机：** 脚本完成后，生成"需要读懂"的画面

| | 说明 |
|---|---|
| **输入** | 图片截图 / 文字描述 / 口播脚本段落 |
| **输出** | 单文件 `.html`，可直接在浏览器打开截图，用作视频 B-roll |
| **保存位置** | `[年月]/[期数]-[slug]/assets/visuals/visual-XX-[描述].html` |
| **用法** | `/html-visual-generator 串行 vs 并行流程对比图，左右分屏，深色背景` |
| **适用场景** | 流程图、对比表、架构图、信息图、数据图、YouTube 封面 |
| **不适用** | 氛围图、场景图、情绪烘托 → 用 seedream |

**判断口诀：** 有精确文字需要读 → HTML；有场景画面要感受 → Seedream

---

### 3. seedream
**触发时机：** 脚本中有"需要感受"的类比/氛围段落

| | 说明 |
|---|---|
| **输入** | 场景描述（中英文均可），尺寸，风格 |
| **输出** | 高质量图片，下载到本地 |
| **保存位置** | `[年月]/[期数]-[slug]/assets/visuals/seedream-[描述].jpg` |
| **用法** | `/seedream 现代工厂并行生产线，科技感，蓝色调，无文字，16:9` |
| **凭据** | `~/.dreamai-env` → `SEEDREAM_ARK_API_KEY` |

---

### 4. libtv-skill
**触发时机：** 需要动态 B-roll 循环动画

| | 说明 |
|---|---|
| **输入** | 动画描述 prompt（参考 style-guide.md 第七章 LibTV 风格前缀） |
| **输出** | `.mp4` 动画文件 |
| **保存位置** | `[年月]/[期数]-[slug]/assets/broll/broll-[描述].mp4` |
| **用法** | `/libtv-skill [风格前缀] + 多线程数据流动画，5秒循环` |
| **风格前缀** | 见 `style-guide.md` 第七章，Cyan #00d4ff 霓虹风格 |

---

### 5. video-checklist
**触发时机：** 脚本和素材清单确认后

| | 说明 |
|---|---|
| **输入** | 视频期数（如 `202603/001`）、脚本文件路径 |
| **输出** | 四阶段 checklist（录制前/录制中/剪辑/发布），内容具体到这条视频的每项任务 |
| **保存位置** | `creator-notes/[年月]/[期数]/checklist.md` |
| **用法** | `/video-checklist 202603/002` |
| **依赖** | 读取 `style-guide.md` 上期复盘改进点（未完成条目） |

---

### 6. youtube-description-generator
**触发时机：** 视频剪辑完成，准备上传前

| | 说明 |
|---|---|
| **输入** | 视频文件路径 |
| **输出** | 完整 YouTube 说明：价值主张 Hook + 精确时间戳章节 + 资源链接 + Tags |
| **用法** | `/youtube-description-generator ~/Movies/my-video.mp4` |
| **技术** | Whisper 转录 → SRT → 章节识别 → Claude 生成说明 |
| **注意** | 时间戳来自 SRT 实际数据，不编造 |

---

### 7. youtube-uploader
**触发时机：** 说明确认后，上传视频

| | 说明 |
|---|---|
| **输入** | 视频路径（必填）、标题（必填）、说明、封面图路径、隐私设置 |
| **输出** | YouTube 链接 `https://youtu.be/xxxxx` |
| **用法** | `/youtube-uploader` 然后按提示填写 |
| **默认隐私** | `private`（上传后在 YouTube Studio 检查再发布） |
| **凭据** | `~/.config/youtube-uploader/client_secret.json` |
| **注意** | OAuth token 绑定频道，首次需浏览器授权，确保选对频道（Rick Ren \| Builds AI） |

**Shorts 要求：**
- 时长 ≤ 60 秒
- 标题包含 `#Shorts`

---

### 8. linkedin-post-generator
**触发时机：** 视频发布后，同步到 LinkedIn

| | 说明 |
|---|---|
| **输入** | 脚本路径 或 SRT 字幕路径 |
| **输出** | LinkedIn 英文 post 文案 + 配套 sketchnote 动态 GIF（1080×1080px）|
| **用法** | `/linkedin-post-generator` |
| **子工具** | `scripts/capture_gif.py` — 生成边框动画 GIF |
| **模板** | `templates/sketchnote-visual-animated.html` — 边框 draw-on 动画 |
| **凭据** | `~/.dreamai-env` → `LINKEDIN_CLIENT_ID` / `LINKEDIN_CLIENT_SECRET` |

---

### 9. video-retrospective
**触发时机：** 视频发布 48 小时后，数据稳定

| | 说明 |
|---|---|
| **输入** | YouTube 视频链接 或 期数 |
| **输出** | 改进点清单，追加到 `style-guide.md # 十一 复盘积累` |
| **用法** | `/video-retrospective https://youtu.be/xxxxx` |
| **对标** | 默认 Nate Herk，可指定其他博主 |
| **作用** | 下期 `video-checklist` 会自动提取未完成改进项提醒 |

---

## 项目目录结构

```
dreamwiseai-demo-series/
├── creator-notes/                    ← git submodule（私有）
│   └── [年月]/[期数]/
│       ├── script.md                 ← 主脚本
│       ├── [slug]-production-pack.md ← video-script-generator 输出
│       └── checklist.md              ← video-checklist 输出
│
└── [年月]/[期数]-[slug]/
    ├── assets/
    │   ├── visuals/                  ← HTML 概念图、Seedream 图、封面
    │   └── broll/                   ← LibTV B-roll MP4
    └── prompts/                     ← Demo 用 prompt 文件
```

---

## 频道信息

| 项目 | 值 |
|------|-----|
| 频道名 | Rick Ren \| Builds AI |
| YouTube | https://www.youtube.com/@rickbuildsAI |
| LinkedIn | https://www.linkedin.com/in/madong-ren-3143b9132/ |
| 网站 | https://dreamwiseai.com |
| 邮箱 | consulting@dreamwiseai.com |
| Google 账号 | madongchn@gmail.com |

---

## 参考文件

| 文件 | 用途 |
|------|------|
| `video-production/style-guide.md` | 制作规范（字体、配色、B-roll、剪辑） |
| `video-production/oral-style-guide.md` | 口播风格（短句、停顿、👉 用法） |
| `video-production/brand-kit.md` | 频道品牌（slogan、定位、认知标签） |
| `video-production/cover-guide.md` | YouTube 封面设计规范 |
