# 上下文文档模板与示例

## 一、上下文文档完整模板

```markdown
# 项目上下文

> 生成时间：{timestamp}
> 对话轮次：{conversation_turns}

---

## 项目信息

| 项目 | 内容 |
|------|------|
| 工作目录 | `{working_dir}` |
| Git 仓库 | `{git_remote}` |
| 当前分支 | `{current_branch}` |
| 主分支 | `{main_branch}` |

## 项目背景

{project_background}

## 当前任务

{current_task}

**状态**: {status} | **优先级**: {priority}

## 进度概览

### 已完成
- [x] {completed_task_1}
- [x] {completed_task_2}

### 进行中
- [ ] {in_progress_task}

### 待办事项
- [ ] {todo_1}
- [ ] {todo_2}

## 技术栈

| 分类 | 技术 |
|------|------|
| 前端 | {frontend} |
| 后端 | {backend} |
| 数据库 | {database} |
| 部署 | {deployment} |
| 其他 | {others} |

## 重要决策

| 决策 | 原因 |
|------|------|
| {decision_1} | {reason_1} |
| {decision_2} | {reason_2} |

## 文件变更

### 新增文件
- `{file_path}` - {description}

### 修改文件
- `{file_path}` - {changes}

### 删除文件
- `{file_path}` - {reason}

## 关键代码位置

| 功能 | 文件:行号 |
|------|-----------|
| {feature} | `{file}:{line}` |

## 遗留问题

- {issue_1}
- {issue_2}

## 下次继续

建议从以下内容开始：
1. {next_action_1}
2. {next_action_2}

## 快速恢复命令

```bash
# 恢复上下文的常用命令
{useful_commands}
```
```

## 二、完整填写示例

```markdown
# 项目上下文

> 生成时间：2025-01-19 14:30:00
> 对话轮次：42

---

## 项目信息

| 项目 | 内容 |
|------|------|
| 工作目录 | `/Users/user/projects/myapp` |
| Git 仓库 | `https://github.com/user/myapp` |
| 当前分支 | `feature/user-auth` |
| 主分支 | `main` |

## 项目背景

这是一个智能客服系统，支持多轮对话和人工接管。目前处于开发阶段，正在实现用户认证模块。

## 当前任务

实现 JWT 认证功能，包括登录、登出、token 刷新。

**状态**: 进行中 | **优先级**: P0

## 进度概览

### 已完成
- [x] 创建项目基础结构
- [x] 配置开发环境
- [x] 实现用户数据模型
- [x] 实现密码加密功能
- [x] 创建认证 API 接口

### 进行中
- [ ] 实现 JWT token 生成和验证

### 待办事项
- [ ] 实现 token 刷新机制
- [ ] 添加认证中间件
- [ ] 编写单元测试
- [ ] 更新 API 文档

## 技术栈

| 分类 | 技术 |
|------|------|
| 前端 | React 18 + Vite + Tailwind |
| 后端 | Node.js + Fastify |
| 数据库 | PostgreSQL + Prisma |
| 部署 | Kubernetes |
| 其他 | JWT, Redis |

## 重要决策

| 决策 | 原因 |
|------|------|
| 使用 Fastify 而非 Express | 性能更好，内置 JSON Schema 验证 |
| 使用 Prisma ORM | 类型安全，迁移管理方便 |
| JWT 存储在 HttpOnly Cookie | 更安全，防止 XSS |

## 文件变更

### 新增文件
- `backend/src/modules/auth/auth.controller.ts` - 认证控制器
- `backend/src/modules/auth/auth.service.ts` - 认证服务
- `backend/src/modules/auth/jwt.util.ts` - JWT 工具函数

### 修改文件
- `backend/src/app.ts` - 添加认证路由
- `backend/prisma/schema.prisma` - 添加 User 模型

## 关键代码位置

| 功能 | 文件:行号 |
|------|-----------|
| 登录接口 | `backend/src/modules/auth/auth.controller.ts:15` |
| JWT 验证 | `backend/src/modules/auth/jwt.util.ts:42` |
| 用户模型 | `backend/prisma/schema.prisma:23` |

## 遗留问题

- Token 过期时间设置为多少合适？
- 是否需要实现 refresh token rotation？
- 登出时是否需要将 token 加入黑名单？

## 下次继续

建议从以下内容开始：
1. 实现 JWT token 生成和验证逻辑
2. 添加认证中间件保护路由
3. 编写单元测试确保功能正确

## 快速恢复命令

```bash
# 查看当前状态
git status
git log -5 --oneline

# 运行开发服务器
npm run dev

# 运行测试
npm test

# 查看认证相关代码
ls -la backend/src/modules/auth/
```

---

_此文件由 Claude Code save-context skill 自动生成_
```
