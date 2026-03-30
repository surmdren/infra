---
name: youtube-uploader
description: 一键上传视频到 YouTube：自动转录生成说明（含时间戳章节）+ 上传视频 + 设置封面缩略图。当用户提供视频文件路径并说"上传到YouTube"、"帮我上传视频"、"发布视频"、"upload to youtube"、"upload video"时必须触发。即使用户只说"上传"并给了视频路径也应触发。
---

# YouTube Uploader

完整的 YouTube 发布流程：转录 → 生成说明 → 上传视频 + 封面。

## 前置条件

- `~/.config/youtube-uploader/client_secret.json` 存在（OAuth 凭据）
- 依赖：`pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`
- 首次运行会弹出浏览器授权，之后 token 自动刷新

## 工作流程

### Step 1：收集参数

需要从用户处确认（没提供就问）：
- **视频路径**：必填
- **标题**：必填
- **封面图路径**：可选，通常在 `assets/visuals/cover-v1.png`
- **隐私设置**：`private`（默认）/ `unlisted` / `public`

### Step 2：转录视频，生成说明

参考 `youtube-description-generator` skill 的完整流程：

```bash
mkdir -p /tmp/whisper-$(basename "$VIDEO" | tr ' ' '-')/
pyenv shell 3.10.18 && whisper "$VIDEO" \
  --model small --language en \
  --output_format srt \
  --output_dir /tmp/whisper-$(basename "$VIDEO" | tr ' ' '-')/
```

读取 SRT，识别章节边界，生成完整说明（格式见 youtube-description-generator）。

**频道配置**：读取 `~/.config/youtube-uploader/channel.yml`，获取默认 links、hashtags、privacy 等。

**说明模板：**
```
[价值主张，2-3句，第一句是 hook]

⏱️ Timestamps:
0:00 – ...

🔗 Links:
DreamWise AI → https://dreamwiseai.com
LinkedIn → https://www.linkedin.com/in/madong-ren-3143b9132/
[本期视频相关工具链接，如有]

📧 合作联系：consulting@dreamwiseai.com

#AIAgent #AITools #ClaudeCode
```

生成后**展示给用户确认**，再继续上传。

### Step 3：发布前检查

上传前自动验证以下条件，任何一项失败则停下来告知用户：

- [ ] 视频文件存在且可读
- [ ] 标题不为空
- [ ] 说明包含时间戳（含 `0:00` 字样）
- [ ] 封面文件存在（如有指定）

### Step 4：上传视频

**新视频上传：**
```bash
pyenv shell 3.10.18 && python ~/.claude/skills/youtube-uploader/scripts/upload.py upload \
  "$VIDEO_PATH" \
  --title "$TITLE" \
  --desc "$DESCRIPTION" \
  --thumbnail "$THUMBNAIL_PATH" \
  --privacy "$PRIVACY" \
  --tags MiniMax AIAgent ClaudeCode AITools AIAutomation
```

**更新已上传视频的元数据：**
```bash
pyenv shell 3.10.18 && python ~/.claude/skills/youtube-uploader/scripts/upload.py update \
  "$VIDEO_ID" \
  --title "$TITLE" \
  --desc "$DESCRIPTION" \
  --thumbnail "$THUMBNAIL_PATH" \
  --tags MiniMax AIAgent ClaudeCode AITools AIAutomation
```

上传/更新完成后输出 YouTube 链接：`https://youtu.be/{video_id}`

**Tags 建议规则：**
- 包含视频主角工具名（如 `MiniMax`、`ClaudeCode`）
- 包含通用标签：`AIAgent`、`AITools`、`AIAutomation`、`AITutorial`
- 8-12 个为宜

## 输出

```
✅ 上传完成！
🔗 https://youtu.be/xxxxx
📌 状态：private（可在 YouTube Studio 修改后发布）
```

## 注意事项

- 时间戳必须来自 SRT 实际数据，不能编造
- 说明必须先展示给用户确认再上传
- 默认用 `private` 模式，让用户在 YouTube Studio 检查后手动发布
- 如果 SRT 文件已存在（同一视频转录过），跳过转录直接读取
- upload.py 路径：`~/.claude/skills/youtube-uploader/scripts/upload.py`
