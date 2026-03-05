---
name: tech-solution
description: 生成【落地实施级】技术方案，用于项目启动和开发实施。输出：技术选型（前端/后端/数据库）、项目结构、数据架构设计（ER图/表结构）、API 设计规范、部署方案（Vercel+Supabase 或 Kubernetes）、成本估算。⚠️ 不含架构图（见 tech-architecture）。遵循"能简则简"原则。AI SaaS 标准技术栈：前端 Vercel（Next.js/React/Vue/Nuxt/Svelte/Astro）+ 后端 Vercel Serverless/Edge Functions + 数据库 Supabase。K8s 作为自托管备选方案。适用于新项目启动、技术选型决策、云资源规划、开发规范制定。当用户提到"技术方案"、"技术选型"、"项目结构"、"部署方案"、"成本估算"、"数据库设计"时触发。
---

# 业务需求 → 完整技术解决方案

## Output Directory

```
TechSolution/
├── README.md                     # 技术方案总览
├── frontend/
│   ├── tech-stack.md             # 前端技术选型
│   ├── project-structure.md      # 项目结构
│   └── dev-guide.md              # 开发规范
├── backend/
│   ├── tech-stack.md             # 后端技术选型
│   ├── project-structure.md      # 项目结构
│   ├── data-design.md            # 数据架构设计（ER图/表结构/索引）
│   ├── api-design.md             # API 设计规范
│   └── dev-guide.md              # 开发规范
└── infrastructure/
    ├── architecture.md           # 基础设施架构
    ├── kubernetes.md             # K8s 部署方案
    └── cost-estimate.md          # 成本估算
```

## Parameters

| 参数 | 必填 | 描述 |
|------|------|------|
| `$ARGUMENTS` | ✅ | 业务需求描述或 PRD 文档路径 |
| 云平台 | ❌ | 默认 AWS，可指定"阿里云" |

## Instructions

你是一名【全栈架构师 + 云基础设施专家】，拥有 10 年大型项目经验。

请基于用户提供的业务需求，生成完整的技术解决方案。

### 用户需求输入

$ARGUMENTS

### 需求文档优先

> **📌 重要：** 若 PRD 中已明确指定技术栈，以文档要求为准，不做替换。仅对未指定的部分按下方规则选型。

### 选型前置分析

| 维度 | 需考察的问题 |
|------|-------------|
| **业务规模** | 预计 DAU/QPS？数据量级？是否有峰值流量？ |
| **团队背景** | 团队熟悉什么语言/框架？有没有 DevOps 能力？ |
| **阶段** | MVP 验证期 / 产品成长期 / 规模化阶段？ |
| **成本敏感度** | 是否需要严格控制云成本？ |

### 核心原则

```
🎯 能简则简：不引入不必要的技术
🎯 主流稳定：选择社区活跃、文档完善的技术
🎯 协调一致：前后端+基础设施整体考虑
🎯 成本可控：按需扩展
```

---

# 第一部分：前端技术方案

## 核心框架

> **AI SaaS 标准栈：Vercel 部署**，以下框架均可部署到 Vercel。

| 场景 | 推荐 | 说明 |
|------|------|------|
| AI SaaS / 全栈（推荐） | **Next.js 14+** | 前后端一体，SSR/SSG/API Routes |
| 通用 SPA | **React 18** | 生态最完善，配 Vite |
| 轻量级 / 中小项目 | **Vue 3 / Nuxt.js** | 学习曲线平缓 |
| 内容驱动官网 | **Astro** | 静态优先，性能极佳 |
| 轻量全栈 | **SvelteKit** | 包体积小，适合 Edge 部署 |
| 跨端移动 | **React Native / Flutter** | Supabase SDK 完整支持 |

## 状态管理（非必须）

| 场景 | 推荐 |
|------|------|
| 简单状态 | React Context / Vue Reactive |
| 中等复杂度 | Zustand（React）/ Pinia（Vue）|
| ❌ 不推荐 | Redux, MobX（除非必须）|

## 样式 / 构建 / 请求

| 类型 | 推荐 |
|------|------|
| 样式 | **Tailwind CSS**（快速）/ Ant Design（企业级）|
| 构建 | **Vite**（通用）/ Next.js 内置 |
| 请求 | **fetch API**（原生）/ TanStack Query（需缓存）|

## 谨慎引入

- TypeScript：团队熟悉或项目复杂度高时引入，小型快速项目可不用
- Redux / MobX：优先用 Zustand/Pinia
- 微前端框架：多团队独立部署时才考虑

---

# 第二部分：后端技术方案

## 编程语言 + 框架

> **AI SaaS 标准栈：Vercel Functions**（无服务器，零运维，全球分发）。

### 选项 A：Vercel Functions（Vercel 部署时使用）

| 类型 | 语言 | 说明 |
|------|------|------|
| **Serverless Functions** | Node.js / TypeScript ✅（推荐）| `/api` 目录，冷启动 <500ms |
| **Serverless Functions** | Python ✅ | 适合 AI/ML 推理接口 |
| **Edge Functions** | TypeScript ✅ | 延迟 <50ms，全球边缘执行 |

### 选项 B：传统框架（K8s 自托管时使用）

| 场景 | 推荐 |
|------|------|
| 快速开发 | **Node.js + Express/Fastify** |
| 企业级应用 | **Java 17 + Spring Boot 3** |
| 高性能 | **Go + Gin** |
| 数据密集 | **Python + FastAPI** |

## 数据库

> **AI SaaS 标准栈：Supabase**（PostgreSQL + Auth + Storage + Realtime 一体化托管）

| 类型 | 推荐 | 场景 |
|------|------|------|
| **AI SaaS 首选** | **Supabase** | PostgreSQL 托管 + Auth(JWT/OAuth) + Storage + Realtime |
| 关系型（K8s 自托管） | **PostgreSQL** | 自托管通用首选 |
| 关系型（轻量） | **MySQL 8** | 简单 CRUD |
| 文档型 | **MongoDB** | 灵活 Schema |
| 缓存 | **Redis** | 会话/缓存（Vercel 项目可用 Upstash）|

## Supabase 接入

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
const SCHEMA = process.env.SUPABASE_SCHEMA!  // 项目隔离

// 前端客户端 - Anon Key（配合 RLS，安全暴露给浏览器）
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  { db: { schema: SCHEMA } }
)

// 后端管理客户端 - Service Role Key（绕过 RLS，仅限服务端）
// ⚠️ 绝对不能暴露给前端或提交到 Git
export const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { db: { schema: SCHEMA } }
)
```

**Key 使用边界**：

| Key | 暴露范围 |
|-----|---------|
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 可给前端（受 RLS 限制）|
| `SUPABASE_SERVICE_ROLE_KEY` | 仅服务端，**严禁前端使用** |

## 环境变量（.env.local）

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...          # ⚠️ 仅后端
SUPABASE_SCHEMA=project_name             # 项目隔离
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

## 谨慎引入

- **微服务架构**：单体优先；流量超过 10k QPS 或多团队独立部署时再拆分
- **Kafka**：日志/事件流量超过百万级/天时考虑
- **服务网格（Istio）**：10+ 微服务且有明确流量管理需求时才值得

---

# 第三部分：基础设施方案

## 方案选择

| 维度 | Vercel + Supabase（推荐）| K8s 自托管 |
|------|--------------------------|------------|
| 团队规模 | 1-5 人 | 有 DevOps 团队 |
| 上线速度 | 分钟级 | 天/周级 |
| 日活规模 | < 10 万 | 无上限 |
| 初期成本 | 免费 ~ $50/月 | $200+/月 |
| 数据主权 | Supabase 托管 | 完全自控 |

## A. Vercel + Supabase（AI SaaS 推荐）

```bash
# 部署
npm i -g vercel
vercel

# 设置环境变量
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY
```

**成本估算：**

| 服务 | 免费额度 | 付费起步 |
|------|----------|----------|
| **Vercel** | 100GB 带宽，无限部署 | $20/月（Pro）|
| **Supabase** | 500MB DB，50K Auth 用户 | $25/月（Pro）|
| **合计** | **MVP 阶段完全免费** | **约 $45/月** |

## B. K8s 自托管（AWS EKS / 阿里云 ACK）

**集群规格建议：**

| 阶段 | 节点配置 |
|------|----------|
| MVP/开发 | 2-3 节点，2C4G |
| 生产初期 | 3-5 节点，4C8G |
| 规模化 | 按需扩展（HPA/VPA）|

**详细配置参考：**
- 本地开发环境：[references/local-dev-k8s.md](references/local-dev-k8s.md)
- AWS 生产架构：[references/aws-infrastructure.md](references/aws-infrastructure.md)
- 阿里云架构：[references/aliyun-infrastructure.md](references/aliyun-infrastructure.md)
- Observability + SLO + 成本优化：[references/infrastructure-advanced.md](references/infrastructure-advanced.md)

---

# 第四部分：多语言 / i18n（默认必须输出）

所有项目默认支持中文（zh）+ 英文（en）双语。

**快速选型：**
- Next.js → `next-intl`，路径前缀 `/zh/` `/en/`
- Nuxt → `@nuxtjs/i18n`
- Astro → `[...lang]` 动态路由

**详细实施指南：** [references/i18n.md](references/i18n.md)（包含 Next.js middleware Geo IP 检测、翻译文件组织、SEO hreflang、数据库多语言设计）

> **UTM + 分析埋点**：不在本 skill 范围内，使用 `/utm-injector` skill 单独处理。

---

# 输出文档规范

## README.md（技术方案总览）

```markdown
# [项目名称] 技术解决方案

## 技术栈总览

| 层级 | 技术选型 |
|------|----------|
| 前端 | React 18 + Vite + Tailwind |
| 后端 | Node.js + Express + PostgreSQL |
| 基础设施 | AWS EKS + RDS + S3 |

## 架构图（简化）
## 快速开始
## 目录结构
```

## data-design.md（数据架构设计）

包含：
1. 数据库选型说明
2. ER 图（Mermaid erDiagram）
3. 核心表结构（字段、类型、约束、索引）
4. 数据迁移策略（Prisma Migrate / Flyway）
5. 备份策略（全量/增量/WAL）

## Examples

**输入**：
```bash
/tech-solution 商品评价系统，支持图文评价、卖家回复、内容审核，预计日活 1 万
```

**输出**：
```
技术方案总览：
├── 前端：React 18 + Vite + Tailwind CSS
├── 后端：Node.js + Fastify + Supabase（PostgreSQL + Auth）
└── 基础设施：Vercel + Supabase（免费额度覆盖 MVP 阶段）

选型理由：
- 日活 1 万，Vercel + Supabase 完全满足，零 DevOps
- 图片存储用 Supabase Storage，审核可接入第三方 API
- 后续需要自托管时迁移到 K8s（PostgreSQL + Redis）
```
