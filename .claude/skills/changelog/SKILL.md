---
name: changelog
description: 根据Git提交记录自动生成CHANGELOG.md，支持语义化版本管理（Semantic Versioning）。分析commit类型（feat/fix/docs/refactor等），按版本组织发布记录，生成符合规范的changelog。适用于版本发布、发布说明生成、变更历史管理。当用户提到"changelog"、"版本发布"、"发布说明"、"变更日志"时触发。
---

# Changelog 自动生成器

## Overview

根据 Git 提交记录自动生成符合规范的 CHANGELOG.md，支持语义化版本管理。

```
1. 分析 Git 提交记录
2. 按提交类型分类（feat/fix/docs/refactor等）
3. 确定版本号（遵循语义化版本）
4. 生成 CHANGELOG.md
5. 创建 Git Tag
6. 生成发布说明
```

## 语义化版本

```
MAJOR.MINOR.PATCH

例：1.2.3
- MAJOR (1): 不兼容的 API 变更
- MINOR (2): 向后兼容的功能新增
- PATCH (3): 向后兼容的问题修复
```

## Conventional Commits

支持的提交类型：

| 类型 | 说明 | 版本影响 |
|------|------|----------|
| `feat` | 新功能 | MINOR + 1 |
| `fix` | 问题修复 | PATCH + 1 |
| `docs` | 文档变更 | 无 |
| `style` | 代码格式 | 无 |
| `refactor` | 重构 | 无 |
| `perf` | 性能优化 | PATCH + 1 |
| `test` | 测试相关 | 无 |
| `chore` | 构建/工具 | 无 |
| `ci` | CI 配置 | 无 |
| `BREAKING CHANGE` | 破坏性变更 | MAJOR + 1 |

## Parameters

| 参数 | 必填 | 描述 |
|------|------|------|
| `版本类型` | ❌ | major/minor/patch/auto(自动判断) |
| `范围` | ❌ | 从哪个 tag 开始，默认最后一个 tag |

## Instructions

你是一名【发布工程师 + DevOps 工程师】，拥有 8 年版本管理和发布经验。

### 工作流程

#### Step 1: 分析 Git 历史

**1.1 获取提交记录**

```bash
# 获取自上一个 tag 以来的提交
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%h|%s|%an|%ad" --date=short

# 示例输出：
# abc1234|feat(auth): add JWT token refresh|张三|2024-01-15
# def5678|fix(chat): resolve message order issue|李四|2024-01-14
# ghi9012|docs(api): update authentication docs|王五|2024-01-13
```

**1.2 解析提交信息**

按照 Conventional Commits 规范解析：

```
<type>(<scope>): <subject>

feat(auth): add JWT token refresh
^---^   ^----^   ^----------------
类型    作用域    描述
```

#### Step 2: 分类变更

按提交类型和作用域分类：

```typescript
interface ChangelogEntry {
  type: 'feat' | 'fix' | 'docs' | 'style' | 'refactor' | 'perf' | 'test' | 'chore' | 'ci';
  scope: string;
  subject: string;
  hash: string;
  author: string;
  date: string;
  breaking?: boolean;
}

interface VersionRelease {
  version: string;
  date: string;
  entries: {
    features: ChangelogEntry[];
    fixes: ChangelogEntry[];
    performance: ChangelogEntry[];
    breaking: ChangelogEntry[];
    documentation: ChangelogEntry[];
    internal: ChangelogEntry[];
  };
}
```

#### Step 3: 确定版本号

**3.1 自动判断版本类型**

```bash
# 检查是否有 BREAKING CHANGE
if git log --pretty=%B | grep -q "BREAKING CHANGE:"; then
  VERSION_TYPE="major"
elif git log --pretty=%s | grep -q "^feat"; then
  VERSION_TYPE="minor"
elif git log --pretty=%s | grep -q "^fix"; then
  VERSION_TYPE="patch"
else
  VERSION_TYPE="patch"  # 默认
fi
```

**3.2 计算新版本号**

```bash
# 获取当前版本
CURRENT_VERSION=$(git describe --tags --abbrev=0 | sed 's/v//')

# 计算新版本
MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
PATCH=$(echo $CURRENT_VERSION | cut -d. -f3)

case $VERSION_TYPE in
  major)
    NEW_VERSION="$((MAJOR + 1)).0.0"
    ;;
  minor)
    NEW_VERSION="${MAJOR}.$((MINOR + 1)).0"
    ;;
  patch)
    NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))"
    ;;
esac
```

#### Step 4: 生成 CHANGELOG.md

**4.1 CHANGELOG 格式**

遵循 [Keep a Changelog](https://keepachangelog.com/) 规范，按版本分组，每个版本包含 Added/Changed/Fixed/Performance/Documentation 等章节。

> **完整格式示例**（含普通版本和破坏性变更格式）→ 见 `references/output-examples.md`

**4.2 破坏性变更格式**

如果有 `BREAKING CHANGE`，在版本顶部添加 `### ⚠️ BREAKING CHANGES` 章节，列出变更详情和迁移指南链接。

> **完整破坏性变更示例** → 见 `references/output-examples.md`

#### Step 5: 创建 Git Tag

```bash
# 创建 annotated tag
git tag -a v${NEW_VERSION} -m "Release v${NEW_VERSION}"

# 推送 tag
git push origin v${NEW_VERSION}
```

#### Step 6: 生成发布说明

生成 Markdown 格式的 GitHub Release Notes，包含：Summary、What's New（按模块）、Bug Fixes、Performance、Documentation、统计数据（Commits/Files/Lines）、Contributors、安装命令。

> **完整发布说明模板** → 见 `references/output-examples.md`

## Output

### 目录结构

```
project/
├── CHANGELOG.md              # 主变更日志
├── RELEASE_NOTES.md          # 本次发布说明
└── .git/
    └── refs/tags/
        └── v1.2.0            # Git Tag
```

## Commit 消息规范

格式：`<type>(<scope>): <subject>`，支持 Body 和 Footer（`Closes #123`、`BREAKING CHANGE:` 等）。

> **示例**（feat/fix/BREAKING CHANGE/docs/perf）→ 见 `references/automation-guide.md`

## 配置文件

> **`.versionrc` 配置文件**（类型映射、URL 格式等）→ 见 `references/automation-guide.md`

## Examples

### 示例 1: 自动生成 changelog
```bash
# 用户请求
请生成 changelog

# Claude 执行流程
1. 获取 Git 提交记录
2. 分析提交类型和作用域
3. 判断版本类型（major/minor/patch）
4. 计算新版本号
5. 生成 CHANGELOG.md
6. 创建 Git Tag
7. 生成发布说明
```

### 示例 2: 指定版本类型
```bash
# 用户请求
请发布 minor 版本

# Claude 执行流程
1. 获取当前版本 (如 1.2.3)
2. 计算新版本 (1.3.0)
3. 分析 Git 提交
4. 生成 CHANGELOG.md
5. 创建 v1.3.0 tag
```

### 示例 3: 指定范围
```bash
# 用户请求
请生成从 v1.0.0 到现在的 changelog

# Claude 执行流程
1. 分析 v1.0.0 到 HEAD 的所有提交
2. 按版本组织变更
3. 生成完整的 CHANGELOG.md
```

## 自动化集成

> **GitHub Actions 自动发布工作流** 和 **NPM 包发布** 脚本 → 见 `references/automation-guide.md`

## 最佳实践

1. **Commit 规范**: 严格遵守 Conventional Commits
2. **及时生成**: 每次发布前生成 changelog
3. **版本标签**: 使用 Git Tag 标记版本
4. **链接提交**: 在 changelog 中关联提交 hash
5. **破坏性变更**: 明确标注并提供迁移指南
6. ** contributors**: 感谢贡献者

## 适用场景

- 版本发布
- 生成发布说明
- 变更历史管理
- GitHub Release
- NPM 包发布
- 项目文档维护
