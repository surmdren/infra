---
name: youtube-creator-research
description: 深度分析 YouTube 行业博主的内容策略，提取可复用的选题规律、标题公式、内容框架和制作工具清单。输入行业关键词或博主频道，输出结构化研究报告，帮助用户快速掌握同行业头部创作者的成功模式，为自己的视频创作提供参考。当用户提到"分析 YouTube 博主"、"研究竞品频道"、"学习视频创作"、"YouTube 内容策略"、"博主选题分析"、"视频标题规律"、"内容框架研究"、"youtube-creator-research"时触发。
---

# YouTube 创作者研究

分析行业头部 YouTube 博主的内容策略，提炼可直接复用的选题、标题、框架和工具规律。

## 输入

用户提供以下任意一种：
- **行业关键词**：如"SaaS 产品演示"、"AI 工具测评"、"健身教程"
- **博主频道列表**：YouTube 频道 URL 或频道名
- **两者结合**：先找博主，再深度分析指定频道

## YouTube Data API v3

从 `~/.dreamai-env` 读取 `YOUTUBE_API_KEY`，优先使用 API 获取精准数据。

```bash
source ~/.dreamai-env
# 搜索频道
curl "https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q=[关键词]&maxResults=10&key=$YOUTUBE_API_KEY"
# 获取频道统计
curl "https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id=[channelId]&key=$YOUTUBE_API_KEY"
# 获取频道视频列表（按播放量排序）
curl "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=[channelId]&order=viewCount&maxResults=20&type=video&key=$YOUTUBE_API_KEY"
# 获取视频详细统计
curl "https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet,contentDetails&id=[videoId1,videoId2,...]&key=$YOUTUBE_API_KEY"
```

如果 `YOUTUBE_API_KEY` 不存在，降级为 WebSearch + WebFetch。

## Gemini 视频内容深度分析

从 `~/.dreamai-env` 读取 `GEMINI_API_KEY`，用于深度分析视频内容（转录、Hook结构、叙事逻辑）。

Gemini 原生支持 YouTube URL 作为输入，无需下载视频。在 Step 4（解构内容框架）时调用：

```bash
source ~/.dreamai-env
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"file_data": {"mime_type": "video/youtube", "file_uri": "https://www.youtube.com/watch?v=VIDEO_ID"}},
        {"text": "分析这个视频的内容结构：\n1. 开场Hook（前30秒）用什么方式抓住注意力？\n2. 视频主体分几个部分，每部分大约时长？\n3. 信息密度和节奏（快剪/缓慢讲解）？\n4. 结尾CTA是怎么引导的？\n5. 博主的口播风格（正式/随意/幽默）？\n请用时间线格式输出，如：0:00-0:30 Hook: ..."}
      ]
    }]
  }'
```

**使用时机**：
- 对每个博主取播放量最高的 **1-2 条视频**做 Gemini 深度分析（避免超出 API 配额）
- YouTube API 负责批量获取 metadata（标题、播放量、发布时间）
- Gemini 负责深度解构具体视频的内容结构和叙事风格

如果 `GEMINI_API_KEY` 不存在，Step 4 改为通过 WebFetch 获取视频描述和评论区来推断结构。

## 工作流程

### Step 1：发现行业头部创作者

**优先用 YouTube API**：搜索频道，获取订阅数、视频数等统计数据，找到 5-10 个头部频道。

**降级用 WebSearch**：搜索以下关键词：
- `site:youtube.com "[行业关键词]" channel`
- `"[行业关键词]" youtube top creators 2024`

对每个候选频道记录：
- 频道名、订阅数、总视频数（来自 API `statistics` 字段）
- 近期上传频率
- 代表性视频（用 API 按 `viewCount` 排序取前 20 条）

### Step 2：分析选题规律

对每个博主，分析其**播放量最高的 20 条视频**，提取：

**选题模式：**
- 高播放量视频聚焦的主题类型（教程型、测评型、对比型、故事型、新闻型）
- 哪类话题能持续获得高流量（常青话题 vs 热点话题的比例）
- 受众最关心的痛点/问题是什么
- 是否有系列化内容（系列播放量通常更高）

**发布节奏：**
- 上传频率（每周几条）
- 发布时间规律

### Step 3：提取标题公式

分析高播放量视频的标题，识别常用公式：

| 公式类型 | 示例结构 | 触发心理 |
|---------|---------|---------|
| 数字型 | `X 个方法让你...` | 具体、可预期 |
| 问题型 | `为什么你的...总是失败?` | 好奇心、共鸣 |
| 对比型 | `XX vs YY：哪个更值得...` | 决策焦虑 |
| 结果型 | `我用 XX 天做到了...` | 期望、可复制 |
| 秘密型 | `没人告诉你的 XX 真相` | 信息差、排他感 |
| 教程型 | `完整教程：从零到...` | 实用性 |

对每个博主，列出其最常用的 3 种标题公式，并给出具体例子。

### Step 4：解构内容框架

挑选每个博主播放量最高的 2-3 个视频，分析其内容结构。

**优先用 Gemini**：取其中播放量最高的 1-2 条视频 URL，调用上方 Gemini API 获取精准的时间线分析。

**降级方案**：通过 WebFetch 获取视频页面描述和置顶评论推断结构。

**开场 Hook（前 30 秒）：**
- 用什么方式抓住注意力（悬念、数据、争议、演示结果）
- Hook 的长度和节奏

**视频主体结构：**
- 分几个部分，每部分时长
- 过渡方式（是否有明确的"接下来"引导）
- 信息密度（快节奏 vs 深度讲解）
- 是否有实例/案例/演示

**结尾 CTA：**
- 引导订阅/点赞的话术
- 是否引导观看下一个视频

记录结构时用时间线形式，例如：
```
0:00-0:30  Hook：展示最终成果画面
0:30-1:30  问题/痛点铺垫
1:30-8:00  核心内容（3个步骤）
8:00-9:00  总结+彩蛋
9:00-9:30  CTA
```

### Step 5：整理制作工具清单

从视频描述、评论区、频道简介中提取博主使用的工具：

- **录制**：摄像机/屏幕录制软件
- **剪辑**：剪辑软件（Premiere、Final Cut、DaVinci、CapCut 等）
- **字幕**：自动字幕工具
- **封面**：Canva、Photoshop 等
- **配乐**：版权音乐来源
- **其他**：绿幕、补光灯、麦克风品牌（如有提及）

如果博主没有明确提及，根据视频质量和风格合理推断。

### Step 6：输出研究报告

将以上分析整合为结构化报告，保存到 `research/[行业名]-youtube-research.md`：

```markdown
# [行业] YouTube 创作者研究报告

## 行业概览
- 头部频道列表（订阅数排序）
- 行业整体内容趋势

## 选题规律总结
- 高播放量话题 Top 10
- 常青话题 vs 热点话题建议

## 标题公式库
[按公式类型整理，每种给 3-5 个真实例子]

## 内容框架模板
[提炼 2-3 种可复用的通用框架]

## 制作工具推荐
[按预算分级：入门/进阶/专业]

## 竞品分析矩阵
| 频道 | 订阅数 | 风格 | 擅长话题 | 标题公式 | 发布频率 |
|------|-------|------|---------|---------|---------|

## 可借鉴的成功要素
[3-5 条核心洞察，直接指导自己的视频创作]
```

## 注意事项

- 重点分析**播放量显著高于平均值**的视频，这些才是真正有效的内容
- 标题公式要提炼**结构**，不是直接抄写，要能套用到自己的行业
- 内容框架关注**信息组织逻辑**，不是具体话术
- 工具清单聚焦实用性，不追求最贵，追求适合初学者上手
