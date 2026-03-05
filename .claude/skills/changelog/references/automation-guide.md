# Changelog 自动化与提交规范指南

## 一、Commit 消息规范

### 推荐格式

```bash
# 基本格式
<type>(<scope>): <subject>

<body>

<footer>
```

### 示例

```bash
# 新功能
feat(auth): add JWT token refresh mechanism

- Implement token refresh endpoint
- Add refresh token rotation
- Update documentation

Closes #123

# 问题修复
fix(chat): resolve message order issue in group conversations

Messages were not displayed in correct order when multiple
users sent messages simultaneously.

Fixes #456

# 破坏性变更
feat(api): rewrite authentication API

BREAKING CHANGE: The authentication API has been completely
rewritten. Old endpoints are no longer supported.

Migration guide: docs/migration-v2.md

# 文档
docs(api): update authentication documentation

Added examples for new OAuth2 flow.

# 性能优化
perf(database): optimize query performance

Added indexes on frequently queried columns.
Reduced query time by 40%.
```

## 二、.versionrc 配置文件

在项目根目录创建 `.versionrc` 配置文件：

```json
{
  "types": [
    { "type": "feat", "section": "✨ Features", "hidden": false },
    { "type": "fix", "section": "🐛 Bug Fixes", "hidden": false },
    { "type": "docs", "section": "📚 Documentation", "hidden": false },
    { "type": "style", "section": "💄 Styles", "hidden": false },
    { "type": "refactor", "section": "♻️ Code Refactoring", "hidden": false },
    { "type": "perf", "section": "⚡ Performance", "hidden": false },
    { "type": "test", "section": "✅ Tests", "hidden": false },
    { "type": "chore", "section": "🔧 Chores", "hidden": false },
    { "type": "ci", "section": "👷 CI", "hidden": false }
  ],
  "commitUrlFormat": "https://github.com/example/myapp/commits/{{hash}}",
  "compareUrlFormat": "https://github.com/example/myapp/compare/{{previousTag}}...{{currentTag}}",
  "issueUrlFormat": "https://github.com/example/myapp/issues/{{id}}",
  "userUrlFormat": "https://github.com/{{user}}"
}
```

## 三、GitHub Actions 自动发布

创建 `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Generate Changelog
        run: |
          # 使用 changelog skill
          npm run changelog

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: RELEASE_NOTES.md
          files: |
            CHANGELOG.md
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 四、NPM 包发布

```bash
# 更新 package.json 版本
npm version ${NEW_VERSION} -m "Release v${NEW_VERSION}"

# 生成 changelog
# (changelog skill 生成)

# 发布到 npm
npm publish
```
