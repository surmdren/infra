---
name: youtube-description-generator
description: 给定视频文件路径，自动转录并生成完整的 YouTube 上传说明（含准确时间戳章节）。适用于 YouTube 创作者上传新视频时需要填写说明栏的场景。当用户提供视频文件路径并提到"生成说明"、"YouTube description"、"generate description"、"帮我填说明"、"视频说明"、"timestamps"、"章节时间"、"生成YouTube说明"时，必须触发本 skill。即使用户只是说"帮我填一下"并提供了视频路径，也应触发。
user-invocable: true
---

# YouTube Description Generator

给定视频文件，自动生成 YouTube 上传说明（含精确时间戳章节）。

## 工作流程

### Step 1：转录视频

使用 Whisper 将视频转录为 SRT 字幕文件：

```bash
mkdir -p /tmp/whisper-$(basename "$VIDEO_PATH" | tr ' ' '-')/
pyenv shell 3.10.18 && whisper "$VIDEO_PATH" \
  --model small \
  --language en \
  --output_format srt \
  --output_dir /tmp/whisper-$(basename "$VIDEO_PATH" | tr ' ' '-')/
```

- 如果系统没有 `pyenv`，直接用 `whisper` 命令
- 语言默认 `en`；如果视频是中文，用 `--language zh`
- `small` 模型在速度和精度之间平衡良好；视频超过 30 分钟可用 `base` 加速

### Step 2：读取 SRT，识别章节边界

读取生成的 `.srt` 文件，分析内容，找出主要话题切换点。

**章节边界信号：**
- 过渡短语：`"now let me"`, `"alright"`, `"first"`, `"second"`, `"third"`, `"next"`, `"so"`, `"let's move on"`, `"demo"`, `"here's"`
- 话题从概念讲解切换到 demo，或从一个 demo 切换到下一个
- 结尾的 CTA（`"subscribe"`, `"comment"`, `"if you enjoyed"`）

**时间格式规则：**
- 使用章节第一个字幕块的起始时间
- 格式：`M:SS`（如 `0:00`, `1:28`, `3:58`）——不要用 `00:00:00`

### Step 3：生成 YouTube 说明

按以下结构输出，直接可以复制粘贴：

```
[价值主张，2-3句。第一句是 hook，说明视频核心洞察或悬念。第二句补充为什么值得看。]

⏱️ Timestamps:
0:00 – [章节标题，简短有力，5-7个词]
X:XX – [...]
...

🔗 Links:
[频道/产品相关链接]

#[Tag1] #[Tag2] #[Tag3] #[Tag4] #[Tag5]
```

**写作要求：**
- 价值主张：第一句直接说结论或提出悬念，不要从"In this video"开头
- 章节标题：动词开头或名词短语，避免模糊词（"Introduction", "Part 1"）
- Hashtags：3-5个，与视频主题直接相关，包含核心工具名称

## 输出示例

以下是一个已验证的输出样本（DreamWise AI 001 期）：

```
Most AI tools fix errors. MiniMax M2.7 fixes the system behind the error. I ran it through 3 real tasks to see if it actually works.

⏱️ Timestamps:
0:00 – Does AI actually learn from its mistakes?
0:25 – The problem with reactive AI (Claude, Codex, Gemini)
1:28 – What is an Agent Harness?
2:29 – MiniMax vs others: the Chef A vs Chef B analogy
2:59 – Demo 1: AI Idea Validation Agent
3:58 – Demo 2: 3D Yellowstone Website (one sentence prompt)
4:42 – Demo 3: Apple PDF → 5-sheet Excel Dashboard
5:27 – Trade-offs: MiniMax vs Claude Code
6:08 – My take: a new way to build AI agents

🔗 Links:
MiniMax M2.7 → https://www.minimaxi.com
DreamWise AI → https://dreamwiseai.com

#MiniMax #AIAgent #ClaudeCode #AgentHarness #AITools
```

## 频道默认信息

读取 `~/.config/youtube-uploader/channel.yml`（如存在）获取默认值。

Links 部分默认包含：
- `DreamWise AI → https://dreamwiseai.com`
- `LinkedIn → https://www.linkedin.com/in/madong-ren-3143b9132/`
- 本期视频相关工具链接（如有，视内容添加）

合作联系固定追加：`📧 合作联系：consulting@dreamwiseai.com`

Hashtags 默认包含 `#AIAgent #AITools #ClaudeCode`。

## 注意事项

- 时间戳必须来自 SRT 实际数据，不要根据脚本估算或编造
- 如果 8899 端口已有 HTTP server 在运行（之前用过），Whisper 转录不需要 server，直接跑即可
- 转录完成后，告知用户 SRT 文件路径，方便后续复用（同一个视频不用重复转录）
