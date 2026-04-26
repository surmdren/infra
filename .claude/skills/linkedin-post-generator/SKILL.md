---
name: linkedin-post-generator
description: 根据 YouTube 视频脚本或 SRT 字幕，生成 LinkedIn 英文 post 并自动发布。当用户说"发LinkedIn"、"同步LinkedIn"、"LinkedIn发帖"、"linkedin-post-generator"、"把视频同步到LinkedIn"、"发一篇LinkedIn"时立即触发。不要等用户说出完整指令——只要用户想把视频内容同步到LinkedIn，就应该触发此 skill。
---

# LinkedIn Post Generator

根据视频脚本或 SRT 字幕生成高质量 LinkedIn post，并通过 LinkedIn API 自动发布。

## 路径常量

```
~/.dreamai-env                              ← LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET
~/.config/linkedin-publisher/token.json    ← OAuth token（首次运行后自动生成）
```

Repo 根目录：
```
/Users/rick.ren/github/dreamai/dreamwiseai-demo-series/
```

脚本路径：
```
creator-notes/[年月]/[期数]/script.md   ← 主要内容来源
```

---

## Step 1：确认内容来源

如果用户已指定视频编号或脚本路径，直接使用。如果没有，询问：
> "是哪期视频？（例如：202603/001）"

优先级：
1. `creator-notes/[年月]/[期数]/script.md` — 最完整，包含结构和核心观点
2. SRT 字幕文件 — 脚本不存在时的备选
3. YouTube 视频标题 + 说明 — 最后备选

读取脚本后，同时读取 `creator-notes/[年月]/[期数]/` 下的其他文件获取 YouTube 链接（通常在 checklist.md 或用户直接提供）。

---

## Step 2：生成 LinkedIn Post 文案

### 格式规范（基于 Brij Pandey 70万粉丝验证的规律）

**Hook（第1行，最重要）**
- 永远不以 "I" 开头（LinkedIn 算法降权）
- 15字以内，制造认知落差或反直觉结论
- 优先用这三个模板：
  - 反直觉："Most people [do X]. But [surprising truth]."
  - 现状转折："[Tool/trend] is evolving fast. Most people are still [wrong approach]."
  - 具体问题："Moving from [A] to [B] is harder than it looks."

**正文（4-6 个 key insights）**
- 每个 insight 1-2 句，短段落，空行分隔
- 用具体工具名（MiniMax、Claude Code、LangGraph），不用泛称（"AI model"、"LLM framework"）
- 用 `→` 或 `✅` 做 bullet 符号，不用普通破折号
- 像资深工程师跟同事解释，不学术，不hedging，直接陈述事实

**结尾双 CTA（关键，缺一不可）**
1. **讨论问题**：一个针对读者职业现实的具体问题，引发评论（算法最高权重信号）
   - 好："Which of these bottlenecks have you hit in production?"
   - 差："What do you think?"
2. **关注引导**：固定格式，每帖必加
   ```
   Follow Rick Ren for more hands-on AI agent breakdowns.
   ```
3. **YouTube 链接**（单独一行）

**Hashtags（最后）**
- 3-5 个，放最后一行
- 从 `#AIAgent #AITools #ClaudeCode` 中选，加视频主题相关的

**配图（必须包含）**
- 读取 `references/linkedin-visual-guide.md` 了解配图规范
- 根据 post 核心观点选择配图类型：
  - **静态 PNG**：用 `templates/sketchnote-visual.html` 填内容 → Chrome headless 导出
  - **动态 GIF**（推荐，scroll-stopping）：用 `templates/sketchnote-visual-animated.html` 填内容 → 运行 `scripts/capture_gif.py` 导出
- 尺寸：1080×1080px，GIF 通常 0.2–0.5 MB，远低于 LinkedIn 5MB 限制
- 导出详细命令参考 `references/linkedin-visual-guide.md`

**GIF 导出命令（一键）：**
```bash
python3 /path/to/scripts/capture_gif.py \
  --html /path/to/visual-animated.html \
  --output /path/to/output.gif
```

### 风格要求
- 纯英文
- 不带装饰性 emoji（只用 `→` `✅` `🔹` 做结构符号）
- 专业但不学术，像从业者写给从业者
- 总长度控制在 1300 字符以内

### Post 模板

```
[Hook，反直觉或制造落差，≤15词]

[Insight 1，1-2句，含具体工具名]

[Insight 2，1-2句]

[Insight 3，1-2句]

[Insight 4，1-2句]

[针对读者职业现实的讨论问题？]

Follow Rick Ren for more hands-on AI agent breakdowns.
[YouTube 链接]

[#hashtag1 #hashtag2 #hashtag3]
```

生成后，**先展示给用户确认**，询问是否需要修改，再发布。

---

## Step 3：OAuth 授权（首次运行）

检查 `~/.config/linkedin-publisher/token.json` 是否存在且未过期。

如果不存在，运行授权脚本：

```bash
cd /Users/rick.ren/github/dreamai/my-skills/.claude/skills/linkedin-post-generator/scripts
source ~/.dreamai-env
python3 auth.py
```

脚本会：
1. 打开浏览器跳转 LinkedIn 授权页
2. 用户授权后，浏览器回调 `http://localhost:8080/callback`
3. 自动保存 token 到 `~/.config/linkedin-publisher/token.json`

---

## Step 4：发布到 LinkedIn

用户确认文案后，运行发布脚本：

```bash
cd /Users/rick.ren/github/dreamai/my-skills/.claude/skills/linkedin-post-generator/scripts
source ~/.dreamai-env
python3 publish.py --text "[post文案]" --url "[YouTube链接]"
```

发布成功后输出 LinkedIn post URL，告知用户。

---

## Step 5：记录到 progress.md

发布成功后，将以下信息追加到 `creator-notes/[年月]/[期数]/checklist.md` 的"内容复用"区块：

```
- [x] LinkedIn post 发布：[LinkedIn post URL]，发布时间：[日期]
```
