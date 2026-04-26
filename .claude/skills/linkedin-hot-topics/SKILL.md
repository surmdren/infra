---
name: linkedin-hot-topics
description: 生成LinkedIn英文post并发布。支持三种模式：1）每天从HN/arXiv/微信热点自动抓取生成；2）用户提供微信文章URL或粘贴文章内容，总结生成post；3）用户提供PDF/文本文件，提取框架后结合用户亲身经验生成原创post。配图支持单张GIF或多图轮播。当用户说"生成今日LinkedIn"、"发LinkedIn"、"帮我把这篇文章发到LinkedIn"、"这篇微信文章发LinkedIn"、"linkedin热点"、"帮我发LinkedIn"、"把这个PDF/文件做成LinkedIn"（没有指定视频）时立即触发。
---

# LinkedIn Hot Topics Post Generator

支持三种内容来源模式，其余流程（生成草稿 → 配图 → 发布）完全相同。

## 路径常量

```
~/.dreamai-env                                          ← LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET / WEWE_RSS_FEED_URL
~/.config/linkedin-publisher/token.json                ← OAuth token（首次运行后自动生成）
~/.claude/skills/linkedin-post-generator/scripts/      ← 复用 auth.py / publish.py / capture_gif.py
~/.claude/skills/linkedin-post-generator/references/   ← 复用 linkedin-visual-guide.md
~/github/dreamai/content/linkedin/                     ← 系列进度文件（*-series.md）
~/github/dreamai/content/research/                     ← 研究报告
~/github/dreamai/content/youtube/                      ← YouTube 内容
```

## 系列进度追踪

**每次触发时，先执行以下检查：**

1. 扫描 `~/github/dreamai/content/linkedin/` 下所有 `*-series.md` 文件
2. 找出状态为 `Draft ready` 或 `Pending` 的最早一篇
3. 如果用户说"发下一篇"或"继续系列"，直接续接该篇，无需重新规划
4. 如果是新 PDF，生成新系列文件，命名规则：`[主题关键词]-series.md`

**系列文件更新规则：**
- 草稿确认后：更新对应篇的 Status 为 `Draft ready`，记录选定草稿
- 发布成功后：更新 Status 为 `Published`，填入发布日期
- 每次生成新篇时：读取文件确认当前是第几篇，保持系列连贯性

---

## Step 0：判断内容来源模式

**模式A — 用户提供了微信文章（URL 或粘贴内容）**

判断条件：用户消息中包含 `mp.weixin.qq.com` 链接，或粘贴了中文文章内容。

处理流程：
1. **如果是 URL**：按以下优先级尝试获取正文

   **方法1（优先）— CDP Proxy 读取已打开的 tab：**
   ```bash
   curl -s http://localhost:3456/targets
   ```
   在返回列表中查找目标微信文章的 `targetId`（匹配 url 字段），然后提取正文：
   ```bash
   curl -s -X POST "http://localhost:3456/eval?target=<targetId>" \
     -d 'document.querySelector("#js_content")?.innerText || document.body?.innerText'
   ```
   - 成功条件：CDP proxy 运行中（localhost:3456）且文章已在 Chrome tab 中打开
   - 注意：Chrome debug port 9222 的 `/json` 接口在新版 Chrome 中返回 404，应直接用 3456

   **方法2（备选）— web-access skill 抓取：**
   如果方法1失败（proxy 未运行或文章未在 tab 中），尝试 web-access skill CDP 模式导航到 URL 抓取

   **方法3（最后）— 请用户粘贴：**
   如果以上均失败，告知用户："微信文章需要登录，请在微信中复制全文粘贴给我"，等待用户粘贴

2. **如果是粘贴的文章内容**：直接使用

获取文章内容后，**跳过 Step 1，直接进入 Step 2**，将文章作为唯一内容源。

---

**模式B — 用户没有提供文章（默认热点模式）**

直接进入 Step 1 抓取热点。

---

**模式C — 用户提供了本地文件（PDF / 文本 / 教程）**

判断条件：用户提供了本地文件路径（如 `.pdf`、`.txt`、`.md`），或说"把这个文件做成LinkedIn"。

处理流程：

1. **读取并提取框架**

   根据文件类型提取内容：
   - PDF：使用 pdfminer 提取文字（`from pdfminer.high_level import extract_text`），取前20页
   - 文本/Markdown：直接读取

   从内容中自动识别：
   - 章节标题和结构（§、Part、Chapter、##等标记）
   - 核心主题列表
   - 关键数据点、对比、方法论
   - 目标受众（文件是写给谁的）

2. **动态生成系列规划**

   根据章节数量和主题，自动规划 LinkedIn 系列：

   - **章节 ≤ 5**：每章一篇，共 N 篇
   - **章节 6-10**：合并相近主题，控制在 5-7 篇
   - **章节 > 10**：提炼最高价值的 5-7 个主题，其余合并或舍弃

   每篇规划包含：
   - 篇号（第X篇/共N篇）
   - 主题（一句话）
   - 目标受众（CTO / CEO / 数字化负责人）
   - 核心主张（这篇要让读者记住的一件事）

   向用户展示系列规划：
   > "根据文件结构，我建议分 X 篇发布，这是系列规划：
   > [表格展示每篇主题/受众/核心主张]
   >
   > 要调整篇数或顺序吗？确认后我们从第1篇开始。"

   等用户确认后，每次只生成**当前篇**的草稿，完成后问："准备好生成第2篇了吗？"

3. **收集用户亲身经验（每篇都问）**

   确认系列规划后，针对**当前篇的主题**提问：

   > "第X篇主题是「[主题]」，在生成之前需要你的亲身经历：
   >
   > 1. 在这个话题上，你有什么具体经历或观察？
   > 2. 有没有让你印象深刻的数据或结果？
   > 3. 有什么反直觉或出乎意料的发现？"

   如果用户说"跳过"或"直接生成"：基于文件框架生成，不加第一人称，但在输出后提示："加入你的个人故事会让这篇效果更好。"

4. **融合生成**

   - 用文件提取的**框架和结构**作为骨架
   - 用用户的**亲身经历替换所有具体案例**（如有）
   - 文件中的第三方数据可保留作为背景支撑
   - 不得出现文件原作者的名字或署名

   **跳过 Step 1，直接进入 Step 2（用融合后的内容生成草稿）。**

   **模式C 额外规范：**
   - 每篇 post 只讲一个核心主张，不堆砌信息
   - 系列内各篇受众角度要轮换（不能连续3篇都是同一受众）
   - 不得出现文件原作者的名字或署名

---

## Step 1：并行抓取三个来源

同时运行以下三个抓取任务：

### 1a. Hacker News
运行 `scripts/fetch_hn.py`：
```bash
source ~/.dreamai-env
python3 ~/.claude/skills/linkedin-hot-topics/scripts/fetch_hn.py
```
抓取 HN Top 30，过滤含以下关键词的标题：
`agent, agentic, llm, claude, openai, anthropic, ai, automation, workflow, copilot, gpt, foundation model`

### 1b. arXiv
运行 `scripts/fetch_arxiv.py`：
```bash
python3 ~/.claude/skills/linkedin-hot-topics/scripts/fetch_arxiv.py
```
抓取 cs.AI + cs.MA 最新论文，取前 10 篇标题和摘要。

### 1c. 微信公众号（wewe-rss）
运行 `scripts/fetch_wechat.py`：
```bash
source ~/.dreamai-env
python3 ~/.claude/skills/linkedin-hot-topics/scripts/fetch_wechat.py
```
读取 `WEWE_RSS_FEED_URL`，返回 48h 内的文章列表。

---

## Step 2：AI 筛选最佳热点

综合三个来源的内容，选出**1条**最适合发 LinkedIn 的热点。

筛选标准（按优先级）：
1. **与企业 Agent 转型直接相关** — 帮公司用 AI Agent 提升效率、重构流程
2. **对 CEO/CTO 有决策参考价值** — 不是纯技术细节，而是业务影响
3. **时效性强** — 今天的新闻优于昨天的论文
4. **有反直觉或争议性** — 容易引发讨论

输出：
- 选中的热点标题 + 来源 URL
- 一句话说明为什么选它

---

## Step 3：生成 3 个 Post 草稿

基于选中热点，生成3个不同角度的草稿：

**核心受众（固定，所有草稿必须对准）：企业 CEO / COO / 业务决策者**
- 他们是最终拍板的人，也是 Rick 咨询业务的目标客户
- 不懂代码，但关心效率、成本结构、竞争优势
- 举例用企业流程（交付周期、招聘成本、运营效率），不用技术案例
- 避免技术术语，但不要过度解释——他们很聪明，只是不写代码

**草稿A：商业结果角度**
- 聚焦可量化的业务影响（成本、速度、竞争优势）
- Hook 模板："Your competitors aren't [doing X the old way] anymore."

**草稿B：决策框架角度**
- 帮 CEO 建立判断标准，而不是告诉他们答案
- Hook 模板："Most business leaders ask the wrong question about AI."

**草稿C：行动号召角度**
- 给出具体的下一步，降低"我该怎么开始"的门槛
- Hook 模板："The companies winning with AI all started the same way."

### Post 格式规范（必须遵守）

参考 `~/.claude/skills/linkedin-post-generator/references/linkedin-visual-guide.md`

```
[Hook，≤15词，不以"I"开头]

[Insight 1，1-2句，含具体工具/公司名]

[Insight 2，1-2句]

[Insight 3，1-2句]

[Insight 4，1-2句]

[针对读者职业现实的讨论问题？]

Follow Rick Ren for more hands-on AI agent breakdowns.
[来源链接：仅 HN 或 arXiv 来源才加链接；微信文章（mp.weixin.qq.com）不加链接]

[#AIAgent #AgentDriven #EnterpriseAI]
```

规范要点：
- 总长度 ≤ 1300 字符
- 用 `→` 或 `✅` 做 bullet，不用破折号
- 不带装饰性 emoji
- 具体工具名（Claude、LangGraph、AutoGen），不用泛称

---

## Step 4：展示草稿，等待用户确认

展示3个草稿后询问：
> "选哪个草稿？（A/B/C）需要修改吗？"

等用户确认或提出修改意见，反复修改直到满意。

---

## Step 5：生成配图

根据 post 的 insight 数量自动选择格式：

| 条件 | 格式 |
|------|------|
| ≤ 4 个 insight | 单张动态 GIF |
| ≥ 5 个 insight | 多图轮播（每页一个观点） |

---

### 格式 A：单张动态 GIF

#### 5A-1. 确定图类型
- **对比图**：新旧方法对比 → 适合商业影响/行动指南角度
- **分层架构图**：技术栈、AI演化 → 适合技术洞察角度
- **路线图**：步骤清单 → 适合行动指南角度

#### 5A-2. 生成动态 HTML
修改 `~/.claude/skills/linkedin-post-generator/templates/sketchnote-visual-animated.html`，填入本次内容。

#### 5A-3. 导出 GIF
```bash
python3 ~/.claude/skills/linkedin-post-generator/scripts/capture_gif.py \
  --html /tmp/linkedin-hot-visual.html \
  --output /tmp/linkedin-hot-visual.gif
```

---

### 格式 B：多图轮播（Carousel）

LinkedIn 多图上传后自动变为可滑动轮播，显示 `1/N` 页码。

#### 5B-1. 规划页面结构
```
第 1 页（封面）：Hook 文字 + 视觉冲击图，≤15词，黑底大字
第 2 页：Insight 1，标题 + 2-3行说明 + 图标
第 3 页：Insight 2
...
第 N-1 页：最后一个 Insight
最后一页（CTA）：讨论问题 + "Follow Rick Ren" + dreamwiseai.com
```

#### 5B-2. 生成每页 HTML
为每页单独生成 HTML 文件，命名为 `/tmp/carousel/page_01.html`、`page_02.html`...

视觉规范（每页统一）：
- 黑底 `#0f0f0f`，Cyan `#00d4ff` 强调色
- 1080×1080px 方图
- 左上角页码：`01 / 06`（灰色小字 #555）
- 右下角 **社交信息栏**（替代原来的单行小字），HTML 模板：

```html
<div class="social-footer">
  <span class="social-item">▶ youtube.com/@rickbuildsAI</span>
  <span class="social-item">🌐 dreamwiseai.com</span>
  <span class="social-item">in linkedin.com/in/madong-ren-3143b9132</span>
</div>
```

对应 CSS：
```css
.social-footer {
  position: absolute;
  bottom: 40px; right: 48px;
  display: flex; flex-direction: column; align-items: flex-end;
  gap: 6px;
}
.social-item {
  font-size: 19px; color: #555; letter-spacing: 0.3px;
}
```

#### 5B-3. 批量截图导出 PNG
```bash
mkdir -p /tmp/carousel
for i in $(seq -f "%02g" 1 N); do
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --headless --disable-gpu --no-sandbox \
    --screenshot=/tmp/carousel/full_${i}.png \
    --window-size=1080,1167 \
    "file:///tmp/carousel/page_${i}.html" 2>/dev/null

  python3 -c "
from PIL import Image
img = Image.open('/tmp/carousel/full_${i}.png')
img.crop((0, 0, 1080, 1080)).save('/tmp/carousel/page_${i}.png')
"
done
```
注：`window-size=1080,1167`（比目标高一点），再用 PIL 裁到 1080×1080，避免 Chrome headless 底部留白。`2>/dev/null` 屏蔽 Chrome 的无关警告日志。

确认所有页面 PNG 存在，每张 < 5MB。

---

## Step 6：OAuth 检查

检查 `~/.config/linkedin-publisher/token.json` 是否存在且未过期。

如果不存在或已过期，运行：
```bash
cd ~/.claude/skills/linkedin-post-generator/scripts
source ~/.dreamai-env
python3 auth.py
```

---

## Step 7：发布到 LinkedIn

**单图 GIF：**
```bash
source ~/.dreamai-env
python3 ~/.claude/skills/linkedin-post-generator/scripts/publish.py \
  --text "[确认后的post文案]" \
  --image /tmp/linkedin-hot-visual.gif
```

**多图轮播：**
```bash
source ~/.dreamai-env
python3 ~/.claude/skills/linkedin-post-generator/scripts/publish.py \
  --text "[确认后的post文案]" \
  --images /tmp/carousel/page_01.png /tmp/carousel/page_02.png /tmp/carousel/page_03.png ...
```

发布成功后输出 LinkedIn post URL，告知用户。
