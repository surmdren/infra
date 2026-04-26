---
name: demo-code-generator
description: 根据视频制作包（production pack）或脚本，自动设计 Live Demo 演示代码和录制脚本。分析视频的 Live Demo 段落，判断每个 Demo 的演示目的（代码审查/生成/转换/调用），设计对应的 demo 代码文件（含有意植入的问题或干净结构），并生成 DEMO-SCRIPT.md 录制参考（中文操作说明 + 英文 prompt）。当用户说"帮我生成 demo 代码"、"准备演示代码"、"生成 demo 脚本"、"demo-code-generator"、"这个视频需要什么 demo"、"帮我设计演示"时触发。
---

# Demo Code Generator

根据视频脚本或制作包，生成可直接用于录制的 demo 代码文件 + 录制操作脚本。

## 路径常量

```
Repo 根目录：/Users/rick.ren/github/dreamai/dreamwiseai-demo-series/
制作包路径：creator-notes/[年月]/[期数]/[slug]-production-pack.md
Demo 输出：creator-notes/[年月]/[期数]/demo/
```

---

## Step 1：读取制作包，定位 Live Demo 段

读取对应视频的 production pack 或 script.md，找出所有 Live Demo 段落，提取：

| 信息 | 用途 |
|------|------|
| Demo 数量和顺序 | 决定生成几套文件 |
| 每个 Demo 的演示目的 | 决定代码设计策略（见 Step 2） |
| 涉及的工具/API/框架 | 决定代码语言和依赖 |
| 预期的 AI 输出（Claude 会看到什么） | 决定代码里植入什么内容 |
| 视频的 Smooth Zoom 时机 | 写入 DEMO-SCRIPT.md |

---

## Step 2：判断 Demo 类型，选择代码设计策略

每个 Demo 的代码设计策略取决于**演示目的**：

### 类型 A — 审查/发现类（Code Review）

**目的**：让 AI 找出问题，展示分析能力
**设计原则**：代码**功能上可运行**，但植入多个维度的问题

植入问题的维度（选 3-5 个，匹配视频主题）：
- **Security**：SQL 注入、硬编码凭证、弱哈希算法（MD5）、无输入校验
- **Performance**：N+1 查询、O(n²) 循环、无索引全表扫描
- **Style**：魔法数字、不清晰命名、PEP8/ESLint 违规
- **Tests**：边界值未测试、错误路径未覆盖
- **Docs**：缺少 docstring/JSDoc

> 参考：`202603/002/demo/app.py` — 5 个维度各埋 1 个问题，Claude Code review 后每维度各返回 1 条发现

### 类型 B — 生成类（Code Generation / Test Generation）

**目的**：让 AI 生成新内容，展示生成能力
**设计原则**：代码**结构清晰、注释完整**，便于 AI 理解和操作

设计要点：
- 函数数量 = 预期 agent 数量（如 Demo B 想展示 10 agents → 写 10 个函数）
- 每个函数有完整 docstring（让 AI 能理解意图）
- 包含边界情况（让生成的测试更丰富）
- 函数之间**独立**（便于并行处理）

> 参考：`202603/002/demo/utils.py` — 10 个独立 utility 函数，各有完整 docstring

### 类型 C — 转换/处理类（Translation / Transformation）

**目的**：让 AI 对现有内容做转换，展示多任务并行能力
**设计原则**：提供**标准、完整**的源文件

设计要点：
- 内容要有代表性（能展示 AI 真正理解了内容）
- 结构清晰（Markdown README、JSON 配置等）
- 适当的长度（太短显不出效果，太长录制拖沓）

> 参考：`202603/002/demo/README.md` — 标准项目 README，用于 Demo C 翻译成 5 种语言

### 类型 D — 调用/集成类（API Call / Tool Use）

**目的**：展示 AI 调用外部 API 或工具
**设计原则**：提供**可运行的脚手架**，让 AI 填充核心逻辑

设计要点：
- 环境变量通过 `.env` 传入（不硬编码 API Key）
- 包含清晰的 TODO 注释标记 AI 需要填写的位置
- 包含基本的错误处理框架

---

## Step 3：生成 Demo 代码文件

根据 Step 2 的策略，为每个 Demo 生成对应文件，保存到：
```
creator-notes/[年月]/[期数]/demo/
```

文件命名规范：
- 主要演示文件：`app.py` / `utils.py` / `main.ts` 等（用常见名，降低认知负担）
- 配置文件：`setup.py` / `.env.example` 等
- 说明文件：`README.md`（若 Demo C 需要）

**代码语言选择**：
- 优先匹配视频主题（讲 Python 工具 → Python，讲 Node 生态 → JS/TS）
- 默认 Python（观众覆盖最广）

**代码质量要求**：
- 能通过语法检查：`python3 -m py_compile *.py`
- 类型 A：植入的问题要**真实**，不能让人一眼看出是假的
- 类型 B：函数要**真正可用**，不是只有签名的占位函数
- 所有代码**只用标准库**（除非视频本身在演示某个第三方库）

---

## Step 4：生成 DEMO-SCRIPT.md

生成录制操作脚本，保存为：
```
creator-notes/[年月]/[期数]/demo/DEMO-SCRIPT.md
```

### 语言规范

| 内容 | 语言 |
|------|------|
| 操作步骤、注意事项、预期画面描述 | **中文** |
| 输入给 AI 的 prompt | **英文**（观众在屏幕上看到） |
| 代码片段、命令 | 保持原样 |

### DEMO-SCRIPT.md 结构模板

```markdown
# Demo 操作脚本（拍摄用）

> 拍摄前：[环境准备说明]

---

## Demo [字母] — [Demo 名称]（[agents 数量] agents）

**目标文件**：`[文件名]`

**操作步骤**：
1. [中文操作说明]
2. 输入以下 prompt（逐字打出，或粘贴）：

\```
[英文 prompt，如需并行末尾加 "These can be done in parallel."]
\```

**预期画面**：
- [中文描述 AI 会做什么]
- [列出关键输出内容]

**Smooth Zoom 时机**：
- [何时放大，停顿多久]

---

## 注意事项

- Demo 顺序：[顺序说明]
- [其他拍摄注意事项]
```

### Prompt 设计原则

- 简洁直接，不超过 3 句话
- 如果需要并行，最后一句必须是：`These can be done in parallel.`
- 用 imperative mood（祈使句）：`Review`, `Write`, `Translate`，不用 `Please` 或 `Could you`
- 明确指定目标文件或范围

---

## Step 5：保存文件并验证

1. 将所有文件保存到 `creator-notes/[年月]/[期数]/demo/`
2. 运行语法检查（Python）：
   ```bash
   cd creator-notes/[年月]/[期数]/demo
   python3 -m py_compile *.py && echo "✓ 语法正常"
   ```
3. 告知用户文件清单和测试方法

**测试 Demo 的方法**：
```bash
cd creator-notes/[年月]/[期数]/demo
claude  # 打开 Claude Code，然后按照 DEMO-SCRIPT.md 输入 prompt
```

---

## 参考案例（202603/002）

| Demo | 类型 | 文件 | Agents | Prompt 关键词 |
|------|------|------|--------|--------------|
| A | 审查类 | `app.py` | 5 | `Review... security, performance, style, tests, docs` |
| B | 生成类 | `utils.py` | 10 | `Write unit tests for every function` |
| C | 转换类 | `README.md` | 5 | `Translate into English, Chinese, Japanese, Korean, Spanish` |
