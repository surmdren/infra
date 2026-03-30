---
name: seedream
description: 用即梦AI（Seedream，火山引擎 Ark 平台）生成氛围图、概念图、背景图。适用于需要「感受」而非「阅读」的视频 B-roll 画面：场景氛围、概念可视化、情绪烘托、封面背景。与 html-visual-generator 的分工原则：需要读懂文字/结构的画面用 HTML，需要感受氛围/场景的画面用 Seedream。凭据从 ~/.dreamai-env 读取 SEEDREAM_ARK_API_KEY。当用户提到"用即梦生成"、"Seedream"、"生成氛围图"、"生成背景图"、"生成概念图"、"生成场景图"、"AI生成图片"、"seedream"时触发。
---

# Seedream 图片生成器

用即梦AI（Doubao-Seedream）生成氛围图、背景图、场景图，用于视频 B-roll 叠加或封面背景。

## 核心判断：用 Seedream 还是 HTML？

| 用 Seedream | 用 html-visual-generator |
|------------|--------------------------|
| 需要「感受」的画面 | 需要「读懂」的画面 |
| 场景/氛围/情绪 | 流程图/对比表/信息图 |
| 概念可视化（厨房、宇宙、城市）| 数据/结构/逻辑展示 |
| 封面背景、过渡画面 | 字幕叠加图、标注图 |

**判断口诀：有精确文字需要读 → HTML；有场景画面要感受 → Seedream**

## 凭据配置

从 `~/.dreamai-env` 读取：

```bash
source ~/.dreamai-env
# 使用变量：$SEEDREAM_ARK_API_KEY
```

## 可用模型

| 模型 | 模型 ID | 免费额度 | 适用场景 |
|------|---------|---------|---------|
| Seedream 5.0 Lite | `doubao-seedream-5-0-lite-260128` | 50张/月 | 默认使用，速度快 |
| Seedream 4.5 | `doubao-seedream-4-5-251128` | 200张/月 | 质量更高，优先保留 |

**默认使用 Seedream 4.5**（免费额度更多）；当用户明确要求 5.0 或 4.5 额度用完时切换。

## API 调用

```bash
source ~/.dreamai-env
curl -s -X POST https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Authorization: Bearer $SEEDREAM_ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "[英文 prompt]",
    "size": "2560x1440",
    "n": 1
  }'
```

**注意：** `size` 最小像素数为 3,686,400（即 2560×1440）。不支持 1920×1080。

返回结果中提取 `data[0].url`，URL 有效期 24 小时，**必须立即下载**。

## 工作流程

### Step 1：理解需求

从用户描述中提取：
- **内容**：要生成什么场景/氛围
- **风格**：科技感/写实/概念艺术/极简
- **用途**：视频哪个段落用/封面背景

如果用于视频 B-roll，自动读取风格指南：
```
../video-production/style-guide.md
```

### Step 2：写英文 Prompt

**视频 B-roll 标准 prompt 结构：**

```
[场景描述], [氛围关键词], [光线/色调], [构图],
cinematic, photorealistic, no text, no people, 16:9 wide shot
```

**视频 B-roll 风格前缀（从 style-guide 提取，自动加上）：**

```
Cinematic, dark background, cyan #00d4ff accent lighting,
dramatic high contrast, premium SaaS aesthetic,
photorealistic, no text overlays, no people
```

**不同场景的 prompt 模板：**

混乱/失败场景（红色调）：
```
[场景], chaotic, fire and smoke, dark dramatic lighting,
red and orange tones, no people, photorealistic, cinematic wide shot
```

高科技/成功场景（Cyan 调）：
```
[场景], futuristic, sleek minimalist design, cyan blue ambient lighting,
clean surfaces, dark background with neon accents, no people, photorealistic
```

概念/抽象场景：
```
[概念] visualization, abstract, glowing particles, deep space background,
cyan energy streams, cinematic, no text, 4K
```

### Step 3：调用 API 并下载

```python
import subprocess, json, urllib.request, os

# 1. 调用 API
result = subprocess.run(['curl', '-s', '-X', 'POST',
    'https://ark.cn-beijing.volces.com/api/v3/images/generations',
    '-H', f'Authorization: Bearer {api_key}',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps({"model": model, "prompt": prompt, "size": "2560x1440", "n": 1})
], capture_output=True, text=True)

data = json.loads(result.stdout)
url = data['data'][0]['url']

# 2. 立即下载（URL 24小时内有效）
urllib.request.urlretrieve(url, output_path)
```

### Step 4：保存路径

视频项目图片保存到：
```
[项目目录]/assets/visuals/seedream-[描述]-[序号].jpg
```

例如：
```
202603/001-minimax-m2.7/assets/visuals/seedream-chef-a-chaotic-kitchen.jpg
202603/001-minimax-m2.7/assets/visuals/seedream-chef-b-hightech-kitchen.jpg
```

### Step 5：通知用户

生成完成后告知：
- 本地文件路径
- 图片尺寸（2560×1440）
- 使用的模型和剩余额度提示
- 如何在视频剪辑中使用（叠加时间点）

## 批量生成

如果用户需要多张图，**串行生成**（避免 API 并发限制），每张间隔 2 秒。

每张生成后立即下载，不等全部完成再下载。

## 常见用途示例

| 视频段落 | 场景描述 | Prompt 关键词 |
|---------|---------|--------------|
| 类比段（失败方） | 混乱厨房 | chaotic kitchen, fire, smoke |
| 类比段（成功方） | 高科技厨房 | futuristic kitchen, cyan lighting |
| Hook 开场 | AI 神经网络 | neural network, glowing nodes, deep space |
| 过渡画面 | 数据流动 | data streams, cyan particles, dark void |
| 观点段 | 闭环系统 | circular energy loop, glowing cyan ring |
| 封面背景 | 科技感背景 | futuristic cityscape, cyan neon, dark sky |

## 注意事项

- URL 24 小时过期，**生成后立即下载**，不要只保存 URL
- Seedream 4.5 每月 200 张免费额度，优先使用
- 生成的图是 2560×1440，视频中使用时在剪辑软件里缩放到 1920×1080
- 不要用 Seedream 生成含精确文字的画面（AI 文字生成不可控）
