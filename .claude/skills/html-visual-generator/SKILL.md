---
name: html-visual-generator
description: 根据图片截图、文字描述或口播脚本段落，生成高质量的 HTML + Tailwind CSS 视觉组件。输出自包含的单文件 HTML，可直接在浏览器中打开，截图后用作视频 B-roll。⚠️ 使用前先判断：需要「读懂」的内容（流程图/对比表/信息图/架构图/数据）用本 skill；需要「感受」的内容（氛围/场景/情绪）用 seedream skill。适用场景：流程图、对比表格、评分卡、信息图、架构图、视频 B-roll 静态画面、数据 Dashboard、时间线、定价表、**YouTube 封面（1280×720，读 cover-guide.md）**、**根据口播脚本逐段生成对应视觉画面**。自动读取 style-guide.md 保证风格统一。当用户提到"生成 HTML 页面"、"做一个流程图"、"做一个对比表"、"生成视觉组件"、"HTML 可视化"、"根据口播生成画面"、"根据脚本生成HTML"、"html-visual-generator"、"还原这张图"、"把这个做成网页"、"做封面"、"YouTube 封面"、"封面设计"时触发。
user-invocable: true
---

# HTML Visual Generator

根据图片截图或文字描述，生成可直接打开的高质量 HTML 视觉组件。

## 风格指南

生成 HTML 组件前，优先读取共享风格指南：
```
../video-production/style-guide.md
```

**如果任务是制作 YouTube 封面**，额外读取：
```
../video-production/cover-guide.md
```
该文件定义了完整的色彩、字体、CDN、架构图节点颜色约定。未指定风格时，以风格指南为准。

## 核心原则

1. **单文件自包含**：所有输出都是一个 `.html` 文件，通过 CDN 引入依赖（Tailwind CSS、Lucide Icons、Google Fonts 等），不依赖本地文件
2. **视觉优先**：输出是给人看的，不是给机器解析的——注重排版、配色、间距、动效
3. **响应式**：桌面和移动端都能正常显示
4. **忠实还原**：如果用户给了参考图，优先还原图片的视觉风格；如果是文字描述，默认使用风格指南的深色科技风

## 技术栈

| 依赖 | CDN | 用途 |
|------|-----|------|
| Tailwind CSS | `https://cdn.tailwindcss.com` | 布局和基础样式 |
| Lucide Icons | `https://unpkg.com/lucide@latest` | 图标库 |
| Google Fonts | `https://fonts.googleapis.com` | 字体 |
| Chart.js | `https://cdn.jsdelivr.net/npm/chart.js`（按需） | 图表 |
| Mermaid | `https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`（按需） | 流程图/架构图 |

只引入实际需要的 CDN，不要全部加载。

## 工作流程

### Step 0：「读 vs 感受」判断

**在生成之前，先判断这个内容是否适合 HTML：**

| 适合 HTML ✅ | 适合 Seedream ❌ |
|-------------|----------------|
| 流程图、步骤图 | 场景氛围图 |
| 对比表、属性表 | 情绪烘托画面 |
| 架构图、节点图 | 概念可视化（厨房、宇宙）|
| 评分卡、数据图 | 封面背景图 |
| 信息图（有文字标注）| 过渡画面 |

如果用户的需求更适合 Seedream，主动告知并建议切换。

**如果来自口播脚本**，逐段判断：
- 这段话说的是「逻辑/流程/数据」→ HTML
- 这段话说的是「场景/比喻/情绪」→ Seedream

### Step 1：理解输入

用户输入可能是：
- **图片截图**：分析图片的布局、配色、字体、图标风格，尽量 1:1 还原
- **文字描述**：理解内容结构，选择最合适的视觉形式
- **口播脚本**：逐段提取需要可视化的信息，生成对应画面
- **两者结合**：以图片为视觉参考，以文字为内容

### Step 2：选择视觉风格

根据内容类型选择合适的风格：

| 内容类型 | 推荐风格 |
|---------|---------|
| 流程图 / 步骤图 | 卡片 + 箭头，柔和背景色分区 |
| 对比表格 | 双列/多列，高亮差异项 |
| 评分卡 / 记分牌 | 大数字 + 进度条 + 颜色编码 |
| 架构图 | 节点 + 连接线，分层布局 |
| 时间线 | 垂直或水平时间轴 |
| 定价表 | 卡片网格，推荐项高亮 |
| 信息图 | 图标 + 数字 + 短文案 |
| Dashboard 卡片 | KPI 数字 + 迷你图表 + 状态指示 |

如果用户没有指定风格，根据内容自动选择最佳方案。

### Step 3：生成代码

生成完整的单文件 HTML，结构如下：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[描述性标题]</title>
  <!-- CDN 依赖 -->
  <style>
    /* 自定义样式（Tailwind 无法覆盖的部分） */
  </style>
</head>
<body>
  <!-- 内容 -->
  <script>
    // 初始化脚本（如 Lucide icons、Chart.js）
  </script>
</body>
</html>
```

**代码质量要求：**
- 使用语义化 HTML 标签
- Tailwind 类名优先，自定义 CSS 仅用于 Tailwind 无法实现的效果（如渐变动画、手绘边框）
- 颜色使用 CSS 变量或 Tailwind 调色板，方便用户后续修改
- 注释标注主要区块，方便用户理解结构

### Step 4：保存和预览

**保存位置优先级：**
1. 如果用户指定了路径，保存到指定路径
2. 如果在项目目录中，保存到 `assets/` 子目录
3. 默认保存到 `/tmp/` 目录

**文件命名：**
- 使用描述性名称：`pricing-comparison.html`、`agent-workflow-flow.html`
- 不要用 `output.html` 或 `index.html`

**预览：**
保存后，如果用户要求预览或暴露到网络：
```bash
python3 -m http.server 8080 --bind [IP] --directory [目录]
```

## 视觉设计参考

### 配色方案

**深色科技风**（适合 B-roll、Dashboard）：
- 背景：`#0f0f0f` 或 `#1a1a2e`
- 强调色：Cyan `#00d4ff`、Magenta `#ff00ff`
- 文字：白色 `#ffffff`

**浅色清爽风**（适合信息图、流程图）：
- 背景：白色或浅灰
- 卡片：柔和色块（蓝 `#dce8f5`、橙 `#f5e6c8`、绿 `#d5e8d4`）
- 文字：深灰 `#374151`

**品牌色风格**（如果用户有品牌色）：
- 直接使用用户指定的颜色

### 字体搭配

| 用途 | 字体 | 场景 |
|------|------|------|
| 手写感标题 | Caveat | 轻松、创意类 |
| 专业标题 | Poppins / Inter | 商务、技术类 |
| 正文 | Inter / Noto Sans SC | 通用 |
| 代码 | JetBrains Mono | 技术展示 |

### 常用效果

- **手绘边框**：双层 border-radius 不规则值 + 内外两层边框
- **毛玻璃**：`backdrop-filter: blur(10px)` + 半透明背景
- **霓虹发光**：`text-shadow` 或 `box-shadow` 配合 Cyan/Magenta
- **渐变背景**：`bg-gradient-to-br` 配合深色调

## 注意事项

- 不要生成完整的 Web 应用（带路由、状态管理等），只生成视觉组件/页面
- 图片内容如果包含具体数据/文字，确保准确转录，不要编造
- 如果用户的参考图包含版权 Logo/品牌元素，用通用替代（如用 Lucide 图标替代）
- 生成后主动告知用户文件路径，方便他们打开预览
