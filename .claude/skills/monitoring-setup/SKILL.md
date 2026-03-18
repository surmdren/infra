---
name: monitoring-setup
description: 为已部署的项目一键配置生产级监控体系。幂等注入 Sentry 错误追踪（前端+后端）、Uptime 监控（UptimeRobot/BetterUptime）、性能告警规则（错误率/响应时间/内存阈值）。生成 Monitoring/monitoring-report.md 报告。应在 dev-deploy 部署完成后执行。当用户提到"配置监控"、"Sentry"、"错误追踪"、"uptime监控"、"告警配置"、"monitoring-setup"、"生产监控"、"监控告警"时触发。
---

# Monitoring Setup

为已部署的 Next.js/Node.js 项目配置完整的生产监控体系。**幂等设计**：每步先检测是否已配置，只添加缺失部分。

## 工作流程

### Step 1: 检测现有监控配置

并行检查：

```
package.json         → 是否有 @sentry/nextjs 或 @sentry/node
sentry.client.config → Sentry 前端是否已初始化
sentry.server.config → Sentry 后端是否已初始化
.env.local / .env    → SENTRY_DSN 是否配置
```

记录检测结果，后续只处理缺失部分。

---

### Step 2: Sentry 错误追踪

#### 2.1 安装依赖（若缺失）

检查 `package-lock.json` / `pnpm-lock.yaml` / `bun.lockb` 判断包管理器：

```bash
npm install @sentry/nextjs    # 或 pnpm add / bun add
```

#### 2.2 初始化 Sentry

运行 Sentry 向导（若 `sentry.client.config.ts` 不存在）：

```bash
npx @sentry/wizard@latest -i nextjs
```

若无法交互，手动创建：

**`sentry.client.config.ts`**：
```typescript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  replaysSessionSampleRate: 0.05,
  replaysOnErrorSampleRate: 1.0,
  integrations: [Sentry.replayIntegration()],
})
```

**`sentry.server.config.ts`**：
```typescript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
})
```

**`sentry.edge.config.ts`**：
```typescript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.1,
})
```

#### 2.3 注入 next.config.js

检查 `next.config.js` / `next.config.mjs` 是否已有 `withSentryConfig`，若无则包装：

```javascript
const { withSentryConfig } = require('@sentry/nextjs')

module.exports = withSentryConfig(nextConfig, {
  silent: true,
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
})
```

#### 2.4 注入错误边界（前端）

在 `app/error.tsx` 中添加 Sentry 上报：

```typescript
'use client'
import * as Sentry from '@sentry/nextjs'
import { useEffect } from 'react'

export default function Error({ error }: { error: Error }) {
  useEffect(() => {
    Sentry.captureException(error)
  }, [error])
  // ...
}
```

#### 2.5 补充环境变量

检查 `.env.local`，追加缺失变量：

```bash
# Sentry
NEXT_PUBLIC_SENTRY_DSN=      # 前端 DSN（从 Sentry 项目设置获取）
SENTRY_DSN=                  # 后端 DSN（同上）
SENTRY_ORG=                  # Sentry 组织 slug
SENTRY_PROJECT=              # Sentry 项目 slug
SENTRY_AUTH_TOKEN=           # CI/CD 用于上传 source maps
```

---

### Step 3: Uptime 监控配置

#### 3.1 生成监控端点列表

读取 `TechSolution/` 或 `app/` 目录，提取需监控的关键 URL：

```
/ (首页)
/api/health (健康检查端点，若无则创建)
/api/auth/session (认证端点)
/{核心功能页} (从 PRD 提取)
```

#### 3.2 创建健康检查 API（若不存在）

在 `app/api/health/route.ts` 创建：

```typescript
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version,
  })
}
```

#### 3.3 输出 UptimeRobot 配置说明

生成 `Monitoring/uptime-config.md`，包含：

```markdown
## UptimeRobot 监控配置

登录 https://uptimerobot.com → Add New Monitor

| 监控名称 | URL | 类型 | 间隔 | 告警阈值 |
|----------|-----|------|------|---------|
| {项目名} Homepage | https://{domain}/ | HTTP | 5分钟 | 2次失败 |
| {项目名} Health API | https://{domain}/api/health | HTTP | 1分钟 | 1次失败 |
| {项目名} Core Page | https://{domain}/{core} | HTTP | 5分钟 | 2次失败 |

告警通知：Email + Slack Webhook（在 Alert Contacts 中配置）
```

---

### Step 4: 告警规则配置

#### 4.1 Sentry 告警规则

输出 `Monitoring/sentry-alerts.md`，说明需在 Sentry Dashboard 手动配置的告警：

**P0 告警（立即通知）**：
- 错误率 > 1% （5分钟窗口）→ PagerDuty/Slack
- 新 Issue 出现 → Slack
- P75 响应时间 > 3s → Slack

**P1 告警（30分钟内通知）**：
- 错误量 > 100/小时 → Email
- Transaction 失败率 > 5% → Slack

---

### Step 5: 生成监控报告

输出 `Monitoring/monitoring-report.md`：

```markdown
# 监控配置报告

## 配置概览

| 监控层 | 工具 | 状态 |
|--------|------|------|
| 错误追踪 | Sentry | ✅ 已配置 |
| Uptime 监控 | UptimeRobot | ⚠️ 待手动创建 |
| 前端性能 | Sentry Performance | ✅ 已配置 |
| 健康检查 API | /api/health | ✅ 已创建 |

## 待完成（需人工操作）

- [ ] 在 Sentry 填写真实 DSN（当前为占位符）
- [ ] 在 UptimeRobot 按 uptime-config.md 创建监控
- [ ] 在 Sentry 按 sentry-alerts.md 配置告警规则
- [ ] 配置 Slack Webhook 到 Sentry Alert Contacts

## 文件变更

| 文件 | 操作 |
|------|------|
| sentry.client.config.ts | 新建 |
| sentry.server.config.ts | 新建 |
| sentry.edge.config.ts | 新建 |
| app/api/health/route.ts | 新建 |
| next.config.js | 修改（withSentryConfig） |
| app/error.tsx | 修改（captureException） |
| .env.local | 追加变量 |
```

## 输出产物

| 文件 | 说明 |
|------|------|
| `sentry.client.config.ts` | Sentry 前端初始化 |
| `sentry.server.config.ts` | Sentry 后端初始化 |
| `sentry.edge.config.ts` | Sentry Edge Runtime 初始化 |
| `app/api/health/route.ts` | 健康检查端点 |
| `next.config.js` | 包含 withSentryConfig |
| `app/error.tsx` | 含错误上报 |
| `.env.local` | 追加 Sentry 变量占位符 |
| `Monitoring/uptime-config.md` | UptimeRobot 配置说明 |
| `Monitoring/sentry-alerts.md` | Sentry 告警规则说明 |
| `Monitoring/monitoring-report.md` | 总体配置报告 |

## 注意事项

1. **凭据阻塞处理**：Sentry DSN 需用户提供 → 写入占位符，写入 `ProjectManager/BLOCKED.md`，继续执行其余步骤
2. **UptimeRobot**：无官方 CLI，输出配置说明文档，由用户手动在 Dashboard 创建
3. **幂等**：每步前先检测对应文件/配置是否存在，避免重复注入
