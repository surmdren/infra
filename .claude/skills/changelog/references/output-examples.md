# Changelog & Release Notes 示例模板

## 一、标准 CHANGELOG.md 格式示例

遵循 [Keep a Changelog](https://keepachangelog.com/) 规范：

```markdown
# Changelog

## 目录

- [简介](#简介)
- [版本变更记录](#版本变更记录)
- [版本链接](#版本链接)

---

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-01-15

### Added
- **auth**: JWT token refresh mechanism (@zhangsan)
- **chat**: Support for file attachments in messages (@lisi)
- **admin**: User management dashboard (@wangwu)

### Changed
- **api**: Rate limiting increased to 100 requests/minute (@zhangsan)
- **database**: Improved query performance with indexes (@lisi)

### Fixed
- **chat**: Message order issue in group conversations (@lisi)
- **auth**: Token expiration not working correctly (@zhangsan)
- **upload**: File upload failure for large files (@wangwu)

### Performance
- Database query optimization reduced response time by 40% (@lisi)
- Implemented Redis caching for session data (@zhangsan)

### Documentation
- Updated API documentation with new endpoints (@wangwu)
- Added deployment guide for AWS EKS (@zhangsan)

## [1.1.0] - 2024-01-01

### Added
- Initial release of customer service system
- Real-time chat functionality
- AI-powered auto-reply
- Agent assignment system

## [1.0.0] - 2023-12-15

### Added
- Project initial release
- User authentication
- Session management

[1.2.0]: https://github.com/example/myapp/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/example/myapp/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/example/myapp/releases/tag/v1.0.0
```

## 二、破坏性变更格式示例（BREAKING CHANGE）

如果有 `BREAKING CHANGE`，在版本顶部添加：

```markdown
## [2.0.0] - 2024-02-01

### ⚠️ BREAKING CHANGES

- **auth**: Authentication API has been completely rewritten
  - Old `/api/auth/login` endpoint removed
  - New endpoint: `/api/v2/auth/login`
  - Request/Response format changed
  - Migration guide: [docs/migration-v2.md](docs/migration-v2.md)

- **database**: Session schema updated
  - `status` field renamed to `state`
  - `priority` field type changed from int to enum

### Added
- New OAuth2 authentication flow
- Multi-factor authentication support

### Changed
- Updated dependencies to latest versions
```

## 三、GitHub Release Notes 完整模板

```markdown
# 🚀 Release v1.2.0

## 📝 Summary

This release includes several new features, bug fixes, and performance improvements.

## ✨ What's New

### 🎫 Authentication
- JWT token refresh mechanism for better security
- Improved token expiration handling

### 💬 Chat
- File attachments support in messages
- Better message ordering in group conversations

### 🎛️ Admin Panel
- New user management dashboard
- Improved search and filtering

## 🐛 Bug Fixes

- Fixed message order issue in group conversations
- Fixed token expiration not working correctly
- Fixed file upload failure for large files

## ⚡ Performance

- Database query optimization - 40% faster response time
- Redis caching for session data

## 📚 Documentation

- Updated API documentation
- Added AWS EKS deployment guide

## 📊 Statistics

- **Contributors**: 3
- **Commits**: 15
- **Files changed**: 42
- **Lines added**: 1,234
- **Lines removed**: 567

## 🔗 Links

- [Full Changelog](https://github.com/example/myapp/blob/main/CHANGELOG.md)
- [Documentation](https://docs.example.com)
- [Migration Guide](https://docs.example.com/migration-v1.2)

## ⬇️ Downloads

- [Source code (zip)](https://github.com/example/myapp/archive/refs/tags/v1.2.0.zip)
- [Source code (tar.gz)](https://github.com/example/myapp/archive/refs/tags/v1.2.0.tar.gz)

## 🙏 Contributors

@zhangsan, @lisi, @wangwu

## ⏱️ Installation

```bash
npm install myapp@1.2.0
# or
yarn add myapp@1.2.0
```
```
