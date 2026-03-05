---
name: save-context
description: 保存当前对话上下文到 .claude/context.md，方便下次对话时用 load-context 快速恢复。提取项目背景、当前任务、已完成工作、待办事项、技术决策等关键信息。适用于长期项目结束前、跨会话工作、项目交接。当用户提到"保存上下文"、"总结进度"、"save context"、"保存进度"、"记录当前状态"时触发。
---

# 对话上下文保存器

## Overview

保存当前对话的上下文信息到 `.claude/context.md`，下次开启新对话时可以快速恢复之前的工作状态。

```
1. 分析当前对话历史
2. 提取关键信息（项目、任务、进度、决策等）
3. 生成结构化上下文文档
4. 保存到 .claude/context.md
```

## 上下文结构

生成的上下文文件包含以下部分：

```markdown
# 项目上下文

## 项目信息
- 项目名称：xxx
- 工作目录：xxx
- 主分支：xxx
- 当前分支：xxx

## 项目背景
[项目的目标和背景]

## 当前任务
[正在进行的任务描述]

## 已完成工作
- [x] 任务1
- [x] 任务2

## 待办事项
- [ ] 任务1
- [ ] 任务2

## 技术栈
- 前端：xxx
- 后端：xxx
- 数据库：xxx
- 部署：xxx

## 重要决策
- [决策1] 原因：xxx
- [决策2] 原因：xxx

## 文件清单
重要文件及其用途

## 下次继续
[下次对话时从哪里开始]
```

## Instructions

你是一名【项目助理 + 技术文档员】，负责整理和保存项目上下文信息。

### 工作流程

#### Step 1: 收集项目信息

通过以下命令收集项目基础信息：

```bash
# 获取 git 远程仓库信息
git remote -v 2>/dev/null || echo "无远程仓库"

# 获取当前分支
git branch --show-current 2>/dev/null || echo "非 git 仓库"

# 获取主分支名称
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main"

# 获取最近 5 条提交
git log -5 --oneline 2>/dev/null || echo "无提交记录"
```

#### Step 2: 分析对话历史

从当前对话中提取以下信息：

1. **项目背景** - 项目是什么，要解决什么问题
2. **当前任务** - 正在做什么
3. **已完成工作** - 已经完成的任务和变更
4. **待办事项** - 还需要做什么
5. **技术栈** - 使用的技术和工具
6. **重要决策** - 做过的技术决策及原因
7. **文件变更** - 修改过的重要文件
8. **下次继续** - 下次对话的建议起点

#### Step 3: 生成上下文文档

使用结构化模板生成上下文，包含项目信息表格、进度概览（已完成/进行中/待办）、技术栈、重要决策、文件变更、关键代码位置、遗留问题、下次继续建议和快速恢复命令。

> **完整上下文文档模板**（含所有字段和完整的填写示例）→ 读取 `references/context-template.md`

#### Step 4: 保存文件

将生成的上下文保存到项目根目录的 `.claude/context.md`：

```bash
# 创建 .claude 目录（如不存在）
mkdir -p .claude

# 保存上下文
cat > .claude/context.md << 'EOF'
{生成的上下文内容}
EOF
```

#### Step 5: 更新 .gitignore

确保 `.claude/context.md` 不会被提交到 git（如果需要）：

```bash
# 检查 .gitignore
if ! grep -q "^\.claude/context\.md" .gitignore 2>/dev/null; then
  echo ".claude/context.md" >> .gitignore
fi
```

## Output

### 输出文件

```
project/
└── .claude/
    └── context.md    # 上下文文件
```

> **完整填写示例** → 见 `references/context-template.md`

## Usage Examples

### 示例 1: 基础用法

```bash
# 用户请求
请保存当前上下文

# Claude 执行
1. 分析对话历史
2. 提取关键信息
3. 生成 .claude/context.md
4. 确认保存成功
```

### 示例 2: 项目中期保存

```bash
# 用户请求
我们今天做了不少工作，帮我总结一下进度

# Claude 执行
1. 列出已完成的工作
2. 记录当前进行中的任务
3. 标记待办事项
4. 保存到上下文文件
```

### 示例 3: 任务切换前保存

```bash
# 用户请求
保存上下文，我要切换到另一个项目

# Claude 执行
1. 完整记录当前项目状态
2. 标记暂停位置
3. 保存下次恢复的建议步骤
```

## 配合使用

### 与 load-context 配合

创建 `load-context` skill 用于恢复上下文：

```bash
# 新对话时
/load-context

# Claude 会读取 .claude/context.md 并快速恢复状态
```

### 自动触发

在 `settings.json` 中配置自动提示：

```json
{
  "hooks": {
    "userPromptSubmit": {
      "command": "save-context",
      "prompt": "对话已进行较长时间，是否保存上下文以便下次恢复？"
    }
  }
}
```

## 最佳实践

1. **定期保存** - 完成重要任务后保存
2. **清晰描述** - 待办事项要具体可执行
3. **记录决策** - 技术决策要记录原因
4. **代码位置** - 关键代码记录文件和行号
5. **下次步骤** - 给出明确的下次行动建议

## 适用场景

- 长期项目的跨会话工作
- 项目交接
- 暂停工作后恢复
- 多项目切换
- 代码审查前准备
