---
name: video-checklist
description: 为 YouTube 视频制作生成专属 Checklist。读取视频脚本和风格指南，自动分析脚本内容，生成包含录制前、录制中、剪辑、发布四个阶段的完整定制化 checklist，并保存到对应视频文件夹。当用户说"生成视频 checklist"、"为这条视频生成 checklist"、"帮我生成制作清单"、"video-checklist"、"制作这条视频的 checklist"、"开始制作视频"时立即触发。不要等用户明确说出 skill 名称才触发——只要用户想为某条具体视频开始制作流程，就应该触发此 skill。
---

# Video Checklist Generator

为指定视频脚本生成完整的制作 Checklist。核心价值在于**根据脚本内容定制每条视频的专属任务**——不是通用模板，而是告诉你这条视频具体需要做哪些 LibTV 画面、哪张架构图、哪个演示文件。

## 路径常量

风格指南路径（优先读取 skill 内置版本）：
```
references/style-guide.md
```

若 skill 目录内找不到，回退到：
```
/Users/rick.ren/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notebooks/01-Area/video-maker/templates/style-guide.md
```

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

## Step 1：确认脚本路径

如果用户已指定脚本路径或视频编号，直接使用。

如果没有指定，询问：
> "请告诉我是哪条视频？（例如：202603/001）"

确认视频路径后，**并行读取**以下两个文件：
- 风格指南（上方固定路径）
- `creator-notes/[年月]/[期数]/script.md`（脚本文件）

---

## Step 2：分析脚本内容

从脚本中提取以下关键信息，这些信息决定了 checklist 的具体内容：

| 信息 | 用途 |
|------|------|
| 视频标题 | checklist 文件头部 |
| Hook 内容（前30秒） | 决定需要哪些 B-roll 素材（LibTV） |
| 核心演示内容 | 决定需要哪些架构图/流程图（Eraser.io/Mermaid） |
| 涉及的 AI 工具 | 决定需要准备哪些 API Key、演示文件 |
| CTA 内容 | 决定片尾导流方向 |

---

## Step 3：生成专属 Checklist

根据风格指南规范 + 脚本具体内容，生成四个阶段。**重点是素材准备部分必须具体到这条视频**——不要写"生成 B-roll"，要写"LibTV 生成 [具体描述] 的动画"。

### 录制前

**环境准备**（参考风格指南「演示沙箱标准化」）
- [ ] VS Code 切换到录屏专用 Profile
- [ ] 隐藏无关文件夹和项目
- [ ] 准备好演示用的 `.env` 文件（列出本视频涉及的具体 API Key）
- [ ] 准备好 Prompt 文件

**素材准备（本视频专属）**
根据脚本 Hook 和演示内容生成具体条目，例如：
- [ ] LibTV 生成 [Hook 中具体描述的视觉效果] 的 B-roll
- [ ] Eraser.io 制作 [具体名称] 架构图（Cyan=输入节点，Magenta=输出节点）
- [ ] 准备好 [具体演示文件，如财报PDF、数据集] 用于实操演示

**设备准备**（参考风格指南「画中画规范」）
- [ ] OBS 场景设置好，测试录屏
- [ ] 手机/相机角度调好，灯光无逆光
- [ ] 麦克风测试无杂音
- [ ] 画中画圆形小窗设置好（右下角，Cyan `#00d4ff` 边框）

**内容准备**
- [ ] Hook 30秒流畅讲出（不用稿纸）
- [ ] 核心演示步骤演练一遍

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

**封面**（参考风格指南「封面模板规范」）
- [ ] Figma 制作封面（1280×720px，深黑背景 `#0f0f0f`）
- [ ] 主标题：Poppins Bold，白色 + Cyan 发光描边（使用脚本中的 Thumbnail Text）
- [ ] 真人照片放左侧（抠图去背景）
- [ ] 包含频道名

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
