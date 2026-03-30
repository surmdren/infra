---
name: video-retrospective
description: 每期 YouTube 视频发布后的复盘工具。分析自己视频的转录内容，对比优秀博主（Nate Herk 等）的内容策略，输出下期可执行的改进点，并追加到 style-guide.md 积累规律。当用户说"视频复盘"、"分析我的视频"、"复盘一下"、"哪里可以优化"、"retrospective"、"这期视频怎么样"、"视频发布后分析"时立即触发。只要用户想回顾刚发布的视频并找改进点，就应该触发此 skill。
---

# Video Retrospective

每期视频发布后运行，目标是从这期视频提炼出**下期能直接用的改进点**，而不是事后批评。

## Step 1：收集输入

需要以下材料（没有就问用户）：

- **YouTube 链接**：优先使用，Gemini 可直接分析视频内容
- **期数/标题**：用于标记复盘记录（如 `202603-001`）
- **对标博主**：默认 Nate Herk，用户可指定其他人

同时读取：
```
creator-notes/video-production/style-guide.md   ← 当前规范
```

## Step 2：用 Gemini 分析视频

Gemini 支持直接传入 YouTube URL 分析视频内容（画面、节奏、人物能量、口播），比单纯读转录稿更全面。

```bash
source ~/.dreamai-env

curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"file_data": {"mime_type": "video/mp4", "file_uri": "YOUTUBE_URL"}},
        {"text": "你是一位专业的 YouTube 内容策略师。请分析这个视频，重点评估：\n1. Hook（前30秒）：第一句话够不够抓人？有没有多余铺垫？\n2. 结构节奏：概念讲解 vs Demo 比例，有没有拖沓段落？\n3. 段落过渡：衔接是否自然？\n4. 主持人能量：镜头前状态、语速、停顿感\n5. CTA：片尾订阅引导是否自然有力？\n请用中文回答，每项给出具体时间戳和改进建议。"}
      ]
    }]
  }' | python3 -c "import sys,json; data=json.load(sys.stdin); print(data['candidates'][0]['content']['parts'][0]['text'])"
```

将 `YOUTUBE_URL` 替换为实际链接（如 `https://youtu.be/DnjhjoIXUYM`）。

如果 YouTube URL 无法直接传入，回退到读取 SRT 文件：从 `/tmp/whisper-*/` 查找，或用户提供路径。

## Step 3：对标博主分析

调用 `youtube-creator-research` skill 分析对标博主的最近 3-5 个视频，重点提取：
- 他们的 Hook 结构（第一句话怎么说）
- 概念讲解时长和方式
- Demo 与讲解的节奏切换
- CTA 措辞

**对比维度**：不是"他们做得好/我做得差"，而是"他们用了什么具体手法，我可以怎么借鉴"。

## Step 4：输出改进点

输出 **3-5 条**改进点，每条必须：
- **具体**：不写"节奏更快"，写"Hook 第一句话控制在 10 秒内，直接说结论"
- **可执行**：下期录制时能直接用
- **有依据**：说明这条建议来自哪里（自己视频的问题 or 竞品的手法）

## Step 5：写入 style-guide.md

将改进点追加到 style-guide.md 末尾的复盘章节：

```markdown
# 十一 复盘积累

## [YYYYMM]-第[NNN]期：[视频标题]
发布日期：[日期]
对标博主：[博主名]

**下期改进点：**
- [ ] [改进点 1 — 依据：...]
- [ ] [改进点 2 — 依据：...]
- [ ] [改进点 3 — 依据：...]
```

如果章节不存在，自动在文件末尾创建。

写入后进入 `creator-notes/` 目录 commit & push：
```bash
cd /Users/rick.ren/github/dreamai/dreamwiseai-demo-series/creator-notes
git add . && git commit -m "retro: 202603-001 复盘改进点" && git push
```

## 输出示例

```
## 202603-第001期：Does MiniMax M2.7 Actually Learn From Its Mistakes?

对标博主：Nate Herk

**下期改进点：**
- [ ] Hook 第一句话去掉 "Do you think..." 改成直接断言或更强的悬念句，参考 Nate Herk 开头直接说"This just changed how I build AI agents"
- [ ] 概念讲解段（Agent Harness）可压缩 30 秒，Demo 1 前的铺垫偏长
- [ ] Demo 之间过渡加一句口头引导，避免"And the second task..."这种生硬开头
- [ ] CTA 加一个具体钩子："下期我会测试 Claude 和 MiniMax 在同一任务上的成本差"
```

## 注意事项

- 改进点要**积累**，不要每期都重置。如果上期的改进点这期还没做，标记出来
- 复盘不是批评，是提炼规律——语气要正向，聚焦"下期怎么做更好"
- 如果这期某个地方做得特别好，也值得记录（"继续保持"类条目）
