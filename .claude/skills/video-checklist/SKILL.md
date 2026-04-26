---
name: video-checklist
description: 为 YouTube 视频制作生成专属 Checklist。读取视频脚本和风格指南，自动分析脚本内容，识别视频结构（概念讲解段 / Live Demo 演示段 / 结尾总结段），分别生成对应的素材清单（HTML visual / Seedream 氛围图 / LibTV B-roll / 屏幕录制），生成包含录制前、录制中、剪辑、发布四个阶段的完整定制化 checklist，并保存到对应视频文件夹。当用户说"生成视频 checklist"、"为这条视频生成 checklist"、"帮我生成制作清单"、"video-checklist"、"制作这条视频的 checklist"、"开始制作视频"时立即触发。不要等用户明确说出 skill 名称才触发——只要用户想为某条具体视频开始制作流程，就应该触发此 skill。
---

# Video Checklist Generator

为指定视频脚本生成完整的制作 Checklist。核心价值在于**根据脚本内容定制每条视频的专属任务**——不是通用模板，而是告诉你这条视频具体需要做哪些 LibTV 画面、哪张架构图、哪个演示文件。

## 路径常量

风格指南路径（共享版本，优先读取）：
```
../video-production/style-guide.md   ← 通用制作规范
../video-production/brand-kit.md     ← 频道品牌专属（slogan、定位、认知标签）
```

若找不到，回退到 skill 内置版本：
```
references/style-guide.md
```

生成 checklist 时同时参考两个文件：style-guide 决定制作规范，brand-kit 决定品牌专属检查项。

Repo 根目录：
```
/Users/rick.ren/github/dreamai/dreamwiseai-demo-series/
```

脚本和 Checklist 放在 `creator-notes/` submodule（私有 repo `creator-notes`），目录结构与 demo-series 一致（年月/期数）：
```
creator-notes/[年月]/[期数]/script.md      # 输入
creator-notes/[年月]/[期数]/checklist.md   # 输出
```

例如 2026年3月第001期视频：
```
/Users/rick.ren/github/dreamai/dreamwiseai-demo-series/creator-notes/202603/001/script.md
/Users/rick.ren/github/dreamai/dreamwiseai-demo-series/creator-notes/202603/001/checklist.md
```

> `creator-notes/` 是 git submodule，指向私有 repo `surmdren/creator-notes`。
> 保存文件后需进入 `creator-notes/` 目录单独 commit & push。

---

## Step 1：确认脚本路径，建立项目目录

如果用户已指定脚本路径或视频编号，直接使用。

如果没有指定，询问：
> "请告诉我是哪条视频？（例如：202603/001，slug 是什么？）"

确认视频信息后，**立即创建标准项目目录**（如果不存在）：

```bash
REPO=/Users/rick.ren/github/dreamai/dreamwiseai-demo-series
YYYYMM=202603          # 年月，如 202603
NO=001                 # 期数，如 001
SLUG=my-video-topic    # 视频 slug（英文，用连字符）

mkdir -p "$REPO/$YYYYMM/$NO-$SLUG/assets/visuals"
mkdir -p "$REPO/$YYYYMM/$NO-$SLUG/assets/broll"
mkdir -p "$REPO/$YYYYMM/$NO-$SLUG/prompts"
```

标准目录结构：
```
[年月]/[期数]-[slug]/
├── assets/
│   ├── visuals/    # 封面 HTML/PNG、图表
│   └── broll/      # B-roll 素材
└── prompts/        # AI 演示提示词
```

创建完成后，**并行读取**以下文件：
- 风格指南（上方固定路径）
- `creator-notes/[年月]/[期数]/script.md`（脚本文件）
- `creator-notes/[年月]/[期数]/director.md`（导演稿，若存在则读取）

读取风格指南后，**额外提取** `# 十一 复盘积累` 章节中**最近一期**的改进点，找出所有 `- [ ]`（未完成）条目，供 Step 3 使用。

> 若 `director.md` 存在，优先从导演稿的「🎬 第三部分：画面与制作」提取每段 B-roll 任务，精度高于从脚本推断。

---

## Step 2：分析脚本内容与视频结构

### 2a. 识别视频结构类型

从脚本判断这条视频包含哪些段落类型：

| 段落类型 | 特征 | 素材需求 |
|---------|------|---------|
| **概念讲解段** | 解释原理/类比/对比/观点 | HTML visual + Seedream + LibTV |
| **Live Demo 演示段** | 真实操作/屏幕录制/工具演示 | 屏幕录制 + 演示文件 |
| **结尾总结段** | Trade-off/观点/CTA | HTML visual + 真人出镜 |

### 2b. 提取关键信息

| 信息 | 用途 |
|------|------|
| 视频标题 | checklist 文件头部 |
| Hook 内容（前30秒） | 决定需要哪些 LibTV B-roll |
| 概念讲解段内容 | 逐段判断 HTML vs Seedream |
| Live Demo 演示内容 | 决定需要哪些演示文件、API Key |
| 类比/场景描述 | 决定 Seedream 生成什么氛围图 |
| CTA 内容 | 决定片尾导流方向 |

### 2c. 素材分配（逐段判断）

对每个段落按以下规则分配素材类型：

- 需要「**读**」（流程/结构/数据/对比）→ **HTML visual**（html-visual-generator）
- 需要「**感受**」（氛围/场景/情绪/类比）→ **Seedream 图片**（seedream skill）
- 需要「**动态**」（循环动画/计数器）→ **LibTV B-roll**（libtv-skill）
- 需要「**真实演示**」→ **屏幕录制**
- 需要「**真人讲解**」→ **真人出镜**

---

## Step 3：生成专属 Checklist

根据风格指南规范 + 脚本具体内容 + 素材分配结果，生成四个阶段。**重点是素材准备部分必须具体到这条视频**——不要写"生成 B-roll"，要写"LibTV 生成 [具体描述] 的动画"。

### 录制前

**视频结构总览**（根据 Step 2a 的分析填写）

```
① [段落名]（时间）→ [概念讲解/Live Demo/结尾]
② [段落名]（时间）→ ...
...
```

**素材准备 — 概念讲解段**

根据 Step 2c 的素材分配，逐段列出：

HTML visual 素材（需要「读」的画面）：
- [ ] `visual-XX-[描述].html` — [对应段落] — [内容说明]

Seedream 素材（需要「感受」的画面）：
- [ ] `seedream-[描述].jpg` — [对应段落] — [场景说明]

LibTV B-roll（动态画面）：
- [ ] `broll-[描述].mp4` — [对应段落] — [动画说明]

**素材准备 — Live Demo 段**

- [ ] 演示文件：[具体文件名和来源]
- [ ] API Key：[列出本视频涉及的具体 Key]
- [ ] Prompt 文件：[列出每个场景的 prompt 文件]
- [ ] Eraser.io 架构图：[如需要，列出具体内容]

**环境准备**
- [ ] VS Code 切换到录屏专用 Profile
- [ ] 隐藏无关文件夹和项目
- [ ] 准备好演示用的 `.env` 文件（列出本视频涉及的具体 API Key）
- [ ] 准备好 Prompt 文件

**素材准备（本视频专属）**

若 `director.md` 存在，从「🎬 第三部分：画面与制作」逐段提取 B-roll 任务：
- [ ] LibTV 生成 [导演稿中 Hook 段 B-roll 描述] → libtv-skill prompt 参考 `style-guide.md` 第七章
- [ ] LibTV 生成 [导演稿中核心演示段 B-roll 描述]
- [ ] Eraser.io 制作 [导演稿中提到的架构图名称]（Cyan=输入节点，Magenta=输出节点）
- [ ] 准备好 [导演稿或脚本中提到的演示文件，如财报PDF、数据集]

若无 `director.md`，回退到从脚本 Hook 和演示内容推断：
- [ ] LibTV 生成 [Hook 中具体描述的视觉效果] 的 B-roll
- [ ] Eraser.io 制作 [具体名称] 架构图
- [ ] 准备好 [具体演示文件] 用于实操演示

**设备准备**（参考风格指南「画中画规范」）
- [ ] OBS 场景设置好，测试录屏
- [ ] 手机/相机角度调好，灯光无逆光
- [ ] 麦克风测试无杂音
- [ ] 画中画圆形小窗设置好（右下角，Cyan `#00d4ff` 边框）

**内容准备**
- [ ] Hook 30秒流畅讲出（不用稿纸）
- [ ] 核心演示步骤演练一遍

**Demo 验证**（仅适用于含 Live Demo 段的视频）

若脚本中有 Live Demo 段，逐场景列出：
- [ ] [场景名] — 完整跑通一遍，确认无报错
- [ ] [场景名] — 测量实际运行时间，更新脚本中的数字
- [ ] 所有场景 Prompt 可直接粘贴，无需现场打字
- [ ] 录制前清空终端历史，确保录屏干净
- [ ] 终端字体调大至 16-18px，确保观众看清代码

**上期复盘待改进项**（来自 style-guide.md `# 十一 复盘积累` 最近一期的未完成条目）

将 Step 1 提取的 `- [ ]` 条目逐条列出，每条前加来源标注：
- [ ] [改进点原文] — ⚠️ 上期遗留

若上期所有条目均已完成（全为 `- [x]`），则写：
> ✅ 上期改进点已全部落实

---

### 录制中

根据脚本四段式结构生成录制顺序（Hook → The Gap → Build → CTA），列出每个段落的具体录制内容：
- [ ] 先录 Hook B-roll（屏幕录制）
- [ ] 录真人出镜 Hook 讲解
- [ ] 录 [具体演示名称] 实操
- [ ] 录对比/结论段落
- [ ] 录 CTA 片段
- [ ] 保留有价值的报错，不要剪掉

---

### 剪辑

**视觉检查项**（参考风格指南「字体规范」「色彩搭配最佳实践」）
- [ ] 字幕：Inter Regular，36–42px，白色+黑色描边
- [ ] 关键词高亮：Cyan `#00d4ff`
- [ ] 中英双语字幕添加
- [ ] 画中画：圆形小窗，右下角，Cyan 边框
- [ ] 关键操作 Smooth Zoom 放大效果（API Key、关键代码行）
- [ ] 动态标注箭头（白色或 Cyan）

**剪辑操作项**（参考风格指南「片头/片尾规范」）
- [ ] 插入 Hook B-roll 素材（LibTV 生成的）
- [ ] 插入架构图/流程图（Eraser.io/Mermaid）
- [ ] 片头：3–5秒 Logo 动画
- [ ] 片尾：推荐视频 + 订阅按钮（15–20秒）
- [ ] 全片流畅播放检查，无跳帧无杂音

---

### 发布

**封面**（参考风格指南「封面规范」+ brand-kit 铁律）
- [ ] 尺寸：1280×720px，背景纯黑 `#0f0f0f`
- [ ] 主标题：Poppins Bold，白色 + Cyan `#00d4ff` 发光描边（从脚本候选标题选最强一个）
- [ ] 真人照片放左侧（抠图去背景）
- [ ] 包含频道名，只用 Cyan 单强调色（⚠️ 封面禁止出现 Magenta）
- [ ] 封面元素不超过 4 个（真人 + 主标题 + 工具Logo/截图 + 频道名）

**封面生成方式（三选一，推荐方式 A）：**
- 方式 A（推荐）：`html-visual-generator` 生成封面 HTML → Chrome headless 导出 PNG
  ```bash
  # 启动本地服务
  cd [封面HTML所在目录] && python3 -m http.server 8899
  # 导出 PNG
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --headless --screenshot=[输出路径]/cover-v1.png \
    --window-size=1280,720 http://localhost:8899/cover-v1.html
  ```
- 方式 B：Figma 手动制作（需要精细调整时）
- 方式 C：libtv-skill 生成底图，再叠加文字：
  ```
  prompt: 深色科技背景 #0f0f0f，Cyan #00d4ff 霓虹发光元素，
  赛博朋克风格粒子特效，16:9，无文字，适合 YouTube 封面底图
  ```
  > 生成底图后在 Figma 叠加标题文字和人物照片

**YouTube 上传**
- [ ] 从候选标题中选最强一个填写
- [ ] 描述填写（含资源/社群链接）
- [ ] Tags 填写（从脚本 Tags 字段复制）
- [ ] 封面上传
- [ ] 字幕文件上传
- [ ] 结束画面设置（推荐视频 + 订阅按钮）

**内容复用**
- [ ] Shorts 裁切（Hook 段，60秒内）
- [ ] 文字稿转图文（Claude 转 LinkedIn/X/公众号）
- [ ] 数据记录到 `video-maker/progress.md`

---

## Step 4：保存文件

将生成的 checklist 保存为：
```
/Users/rick.ren/github/dreamai/dreamwiseai-demo-series/creator-notes/[年月]/[期数]/checklist.md
```

- 如果目录不存在，自动创建
- 示例：`/Users/rick.ren/github/dreamai/dreamwiseai-demo-series/creator-notes/202603/001/checklist.md`

保存完成后，进入 `creator-notes/` 单独 commit & push：
```bash
cd /Users/rick.ren/github/dreamai/dreamwiseai-demo-series/creator-notes
git add . && git commit -m "feat: add checklist for [年月]/[期数]" && git push
```

文件头部格式：
```markdown
# 视频制作 Checklist — [视频标题]
日期：[今天日期]
脚本：[脚本文件名]
```

保存完成后告知用户文件路径，并提示可以开始录制前准备。
