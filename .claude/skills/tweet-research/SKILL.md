---
name: tweet-research
description: Evaluates a Twitter/X tweet URL for authenticity and relevance to a YouTube AI tech channel (DreamWise AI). Reads the tweet via browser, scores it on authenticity and channel value, then either appends a structured entry to the video research library or discards it with a clear reason. Trigger whenever the user shares a tweet URL and asks to evaluate, save, record, research, or check it for the channel. Also trigger when user says things like "帮我记一下这个推文"、"看看这个有没有用"、"这条推文值得记录吗"、"save this tweet"、"is this tweet worth covering".
---

## 目标

判断一条推文是否值得作为 YouTube AI 科技频道（DreamWise AI）的选题或研究素材，并将有价值的内容以结构化格式保存到研究库。

---

## 工作流程

### Step 1：读取推文内容

使用 web-access skill 通过 CDP 打开推文 URL，提取：
- 作者账号和简介
- 推文全文
- 互动数据（点赞、转发、浏览）
- 提到的工具、项目、数据

### Step 2：真实性评估

判断这条内容是否可信：

| 维度 | 判断方法 |
|------|---------|
| **作者可信度** | 是否是已知 AI/开发者圈子的人？简介是否与内容匹配？ |
| **数据可核实** | 提到的 GitHub stars、工具名称、功能是否有一手来源可验证？ |
| **内容是否夸大** | 有没有明显的营销夸大或无法证实的绝对化表述？ |

真实性结论：
- ✅ 可信：作者可信 + 数据可核实
- ⚠️ 存疑：有价值但部分内容需核实，保存时注明
- ❌ 不可信：数据无来源、明显营销号、内容造假 → **直接丢弃**

### Step 3：频道价值评估

判断这条内容对频道的价值，打分 High / Medium / Low：

| 维度 | High | Medium | Low |
|------|------|--------|-----|
| **话题相关性** | AI 工具、Agent、自动化、代码生成 | AI 周边（商业、创业、政策） | 与 AI 无关 |
| **中英信息差** | 中文圈独有，英文圈未覆盖 | 中英都有但角度不同 | 英文圈已烂大街 |
| **Demo 潜力** | 有可视化操作，现场可演示 | 有截图或结果，难以演示 | 纯文字，无法演示 |
| **受众匹配** | MLOps/DevOps/AI 从业者会用 | 广泛 AI 用户感兴趣 | 过于小众或过于泛 |

### Step 4：决策

**保存条件**：真实性 ✅ 或 ⚠️，且价值维度中至少 2 个 High 或 3 个 Medium+

**丢弃条件**（任一满足即丢弃）：
- 真实性 ❌
- 话题相关性 Low
- 所有价值维度均 Low

**存疑处理**：真实性 ⚠️ 的内容保存时在「真实性」字段注明需核实的部分。

### Step 5：输出

**如果保存**，追加到研究文件（路径见下方），格式如下：

```markdown
### [工具/话题名称]
- **来源**：@账号名
- **链接**：推文 URL
- **真实性**：✅/⚠️ （简短说明）
- **内容摘要**：2-3句话概括推文核心内容
- **对频道的价值**：说明为什么值得做，哪个方向最有潜力
- **使用建议**：建议的视频方向、Hook 思路、Demo 场景（1-3条）
```

**如果丢弃**，直接告知用户原因（1-2句），不写入文件。

---

## 研究文件路径

根据当前日期动态确定路径：

```
/Users/rick.ren/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notebooks/01-Area/video-maker/research/YYYYMM/tweet-research.md
```

如果文件不存在，先创建并加上标题：
```markdown
# Tweet 选题研究库

> 用途：记录从 Twitter/X 发现的有价值内容，作为选题、脚本素材和行业洞察

---

## [YYYY-MM-DD]
```

如果文件已存在，检查是否已有当天日期的 `## YYYY-MM-DD` 标题，没有则追加。

---

## 频道定位参考（判断时使用）

- **频道名**：DreamWise AI
- **定位**：AI 工具评测 + 系统化方法论，面向海外英文观众
- **差异化**：把中文圈 AI 新动态用英文讲给海外观众（中英信息差）
- **目标受众**：想提升效率的个人用户、MLOps/DevOps 从业者、独立创业者
- **优质内容特征**：有 Demo 可演示、有数据支撑、海外未广泛覆盖
