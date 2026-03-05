# Jira API 调用示例

## Epic 创建 JSON 示例

```json
{
  "summary": "Epic: 01-数据模型模块",
  "issue_type": "Epic",
  "description": "实现数据库模型设计，包括 User、Session、Message 等核心实体的 Schema 定义和 Repository 实现",
  "priority": "High",
  "labels": ["database", "backend", "foundation"]
}
```

## Task 创建 JSON 示例

**Step 1 → Task**:
```json
{
  "summary": "Task: 设计数据库 Schema (Prisma)",
  "issue_type": "Task",
  "description": "定义 User、Session、Message 等核心实体的 Prisma Schema，设计实体间关系和索引",
  "priority": "High",
  "labels": ["backend", "database", "prisma"],
  "estimate": "4h"
}
```

**Step 2 → Task**:
```json
{
  "summary": "Task: 创建数据库迁移",
  "issue_type": "Task",
  "description": "生成 Prisma 迁移文件并执行数据库迁移",
  "priority": "High",
  "labels": ["backend", "database", "migration"],
  "estimate": "2h"
}
```

## 完整 tickets.json 示例

```json
[
  {
    "summary": "Epic: 01-数据模型模块",
    "issue_type": "Epic",
    "description": "实现数据库模型设计...",
    "priority": "High",
    "labels": ["database", "backend", "foundation"]
  },
  {
    "summary": "Task: 设计数据库 Schema (Prisma)",
    "issue_type": "Task",
    "description": "定义 User、Session、Message 实体...",
    "priority": "High",
    "labels": ["backend", "database", "prisma"],
    "estimate": "4h"
  },
  {
    "summary": "Task: 创建数据库迁移",
    "issue_type": "Task",
    "description": "生成并执行 Prisma 迁移文件...",
    "priority": "High",
    "labels": ["backend", "database"],
    "estimate": "2h"
  },
  {
    "summary": "Epic: 02-认证授权模块",
    "issue_type": "Epic",
    "description": "实现用户认证和授权功能...",
    "priority": "High",
    "labels": ["auth", "backend", "security"]
  },
  {
    "summary": "Task: 实现用户注册 API",
    "issue_type": "Task",
    "description": "实现 POST /api/auth/register...",
    "priority": "High",
    "labels": ["backend", "api", "auth"],
    "estimate": "3h"
  }
]
```

## 依赖关系链接 JSON 示例

```json
{
  "update": {
    "issuelinks": [
      {
        "add": {
          "type": {"name": "Dependency"},
          "inwardIssue": {"key": "EPIC-001"},
          "outwardIssue": {"key": "EPIC-002"}
        }
      }
    ]
  }
}
```

## tickets.json 格式规范

```json
[
  {
    "summary": "Epic: {模块名称}",
    "issue_type": "Epic",
    "description": "{模块描述}",
    "priority": "High/Medium/Low",
    "labels": ["{标签1}", "{标签2}"]
  },
  {
    "summary": "Task: {Step 描述}",
    "issue_type": "Task",
    "description": "{Step 详细说明}",
    "priority": "High/Medium/Low",
    "labels": ["{标签1}", "{标签2}"],
    "estimate": "2h"
  }
]
```
