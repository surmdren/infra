# LinkedIn 配图规范

参考来源：Brij Pandey（70万粉丝，5.3% 互动率，Taplio 100/100）

## 核心原则

LinkedIn 配图的第一优先级是**移动端可读性**——图是内容主体，文字是引子。
配图不是封面，是独立的信息图，读者不看文字只看图也能理解核心观点。

---

## 图的类型（按使用场景）

### 1. 分层架构图（最常用）
适合：技术栈、AI 演化、系统组成
特征：
- 从下到上或从左到右的层次结构
- 每层一个标签，1-3个关键词
- 层与层之间用箭头或分隔线
- 不超过 6 层

示例：Classical AI → Deep Learning → GenAI → Agentic AI

### 2. 路线图 / 步骤图
适合：学习路径、操作流程、技能清单
特征：
- 纵向列表，每步编号
- 每步标题 + 1行说明
- 不超过 7 步

### 3. 对比图
适合：新旧方法对比、工具选型、误区纠正
特征：
- 两列：❌ 错误做法 vs ✅ 正确做法
- 或：Before vs After

---

## 视觉风格规范

### 背景
- 首选：纯黑 `#0f0f0f`（与频道品牌一致）
- 备选：纯白 `#ffffff`（更接近 Brij 风格，移动端对比度高）

### 字体
- 标题：Poppins Bold，28-36px
- 正文标签：Inter Regular，18-22px
- 强调词：Cyan `#00d4ff`（与频道品牌色一致）

### 配色
- 主色：白色文字 + Cyan `#00d4ff` 强调
- 边框/分隔线：Cyan `#00d4ff` 或灰色 `#333333`
- 禁止：渐变、阴影、多色（保持极简）

### 尺寸
- 1:1 方图（1080×1080px）— LinkedIn 最佳展示比例
- 或 4:5 竖图（1080×1350px）— 移动端占屏更多

### 留白
- 四周留白不少于 60px
- 元素间距宽松，不要塞满

---

## 生成方式

用 `html-visual-generator` 生成 HTML，Chrome headless 导出 PNG：

```bash
# 启动本地服务
cd [配图HTML所在目录] && python3 -m http.server 8899

# 导出 1:1 方图
# 注意：Chrome --headless 保留约 87px 给隐藏 UI，viewport 实际只有 993px 高
# 必须用 1080+87=1167 作为 window height，然后 crop 到 1080×1080
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --screenshot=/tmp/linkedin-visual-full.png \
  --window-size=1080,1167 http://localhost:8899/linkedin-visual.html

# 裁剪为标准 1080×1080
python3 -c "
from PIL import Image
img = Image.open('/tmp/linkedin-visual-full.png')
img.crop((0, 0, 1080, 1080)).save('[输出路径]/linkedin-visual.png')
"
```

---

## 署名规范（参考 Brij Pandey）

- Sketchnote 风格：在图内右下角用 Caveat 手写体，斜体，`— Rick Ren`，字号 30px，颜色 `#555`
- 深色极简风格：右上角小字 `@rickbuildsai` 或右下角 `Rick Ren · dreamwiseai.com`，颜色 Cyan
- 署名必须在图内，不能悬浮在内容框外被截断
- 实现方式：用 `position: absolute; bottom: 14px; right: 20px;` 在 conclusion 容器内（conclusion 本身用绝对定位 + 明确 height）

## 什么不要做

- 不要把署名放在 `position: absolute` 且在 body 级别——会被 `overflow: hidden` 截断；必须放在有明确高度的内容容器内
- 不要用 `flex: 1` spacer 推署名到底部——如果内容 + 署名超出容器高度，署名会被 overflow:hidden 截断且不可见
- 不要用 flexbox 控制整体布局高度——用 `position: absolute` 给每个 section 设明确的 `top` + `height`
- 不要用 `--window-size=1080,1080` 导出——Chrome headless 保留约 87px，viewport 实际高度只有 993px，body 会被截断
- 不要用视频封面直接作为 LinkedIn 配图（16:9 比例在 LinkedIn feed 显示效果差）
- 不要超过 4 种颜色
- 不要小于 18px 的正文字体（移动端看不清）
- 不要把太多信息塞进一张图（一图一个核心观点）
