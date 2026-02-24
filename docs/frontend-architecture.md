# 前端架构参考 - Supabase 集成

> 适用于所有 DreamAI 项目的前端架构设计参考

---

## 标准架构（现代 SaaS）

```
┌─────────────────────────────────┐
│         用户 / 浏览器            │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         前端应用                 │
│   Next.js / React / Vue 等      │
│   （Vercel / Cloudflare 部署）   │
└──────────────┬──────────────────┘
               │ Supabase JS SDK
┌──────────────▼──────────────────┐
│           Supabase               │
│  ┌─────────┐  ┌──────────────┐  │
│  │  Auth   │  │  Database    │  │
│  │ 登录认证 │  │ PostgreSQL   │  │
│  └─────────┘  └──────────────┘  │
│  ┌─────────┐  ┌──────────────┐  │
│  │ Storage │  │  Realtime    │  │
│  │ 文件存储 │  │  实时订阅    │  │
│  └─────────┘  └──────────────┘  │
│  ┌─────────────────────────┐    │
│  │   Edge Functions        │    │
│  │   （自定义后端逻辑）      │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

---

## 请求流程

1. 用户登录 → Supabase Auth 验证，返回 JWT Token
2. 前端带着 Token 直接查数据库 → RLS 自动过滤权限
3. 上传文件 → 直接传到 Supabase Storage
4. 复杂逻辑（支付/发邮件/第三方集成）→ 调 Edge Function

---

## 后端层级选择

### 简单项目（推荐起步）
```
前端 ──直连──▶ Supabase
```
- 完全不需要自己写后端
- Auth、权限、存储全部 Supabase 处理
- 适合 MVP 和早期验证

### 复杂项目（业务逻辑多）
```
前端 ──▶ 自己的后端 API（Node/Python）──▶ Supabase
前端 ──直连──▶ Supabase（简单查询）
```
- 加一层轻量后端处理第三方集成
- 敏感逻辑不暴露给前端

---

## AI Agent 项目架构

```
用户对话界面（前端）
        │
        ▼
AI Agent 服务（Python / Node）
        │
        ▼
┌───────────────────────┐
│       Supabase         │
│  - 对话历史            │
│  - 用户信息            │
│  - 向量搜索(pgvector)  │
│  - 文件存储            │
└───────────────────────┘
```

---

## 支持的前端技术栈

### 官方 SDK
- JavaScript / TypeScript（最完整）
- Python
- Swift（iOS / macOS）
- Kotlin（Android）
- Flutter / Dart

### 前端框架（通过 JS SDK）
- Next.js ✅（推荐，SSR 支持最好）
- React ✅
- Vue / Nuxt.js ✅
- Svelte / SvelteKit ✅
- Angular ✅
- Remix ✅
- Astro ✅

### 社区 SDK
- C# / .NET / Unity
- Go、Rust、PHP、Ruby

> 本质：Supabase 底层是标准 REST API + GraphQL + WebSocket，
> 任何能发 HTTP 请求的语言都可以集成。

---

## 核心优势

- ✅ 省掉自己写 Auth、权限、文件系统
- ✅ 前端可直连，减少后端复杂度
- ✅ 实时功能（Realtime）开箱即用
- ✅ Row Level Security 数据库级别权限控制
- ✅ pgvector 支持 AI 向量搜索

---

## DreamAI 项目接入

各项目连接同一个 Supabase 实例，通过独立 schema 隔离：

```
前端项目 A → Supabase（schema: project_a）
前端项目 B → Supabase（schema: project_b）
```

详见 [architecture.md](./architecture.md) 中的多项目 Schema 隔离方案。

---

## 适用场景评估

### ✅ 能很好支撑的（90% 的应用）

- SaaS 工具类（CRM、项目管理、表单、仪表板）
- AI 产品（聊天机器人、Agent、RAG 知识库）
- 内容平台（博客、社区、论坛）
- 电商（中小规模）
- 移动 App（iOS / Android / Flutter）
- 内部工具、后台管理系统
- 实时协作（文档、白板）

### ⚠️ 能支撑但需要额外补充

- **高并发电商**（双11级别）→ 需要加缓存层（Redis）
- **复杂支付流程** → 需要独立后端处理 Stripe / 支付宝
- **视频流媒体** → Storage 不适合大视频，需要 CDN
- **复杂推荐算法** → 需要独立 ML 服务

### ❌ 不适合的场景（少数）

- 超高频交易系统（金融、秒杀）→ 需要专用数据库
- 重计算任务（视频转码、模型训练）→ 需要 GPU 服务器
- 游戏服务端（低延迟状态同步）→ 需要专用 Game Server

### 扩容节点

> 这套架构可以支撑从 0 到百万用户级别，不需要换架构，只需根据流量扩容节点。

| 规模 | 建议动作 |
|------|---------|
| 月活 < 100万 | 当前架构足够，专注产品 |
| 月活 > 100万 | 考虑读写分离 |
| 数据量 > 1TB | 考虑分库分表 |
| 并发 > 10,000 QPS | 加缓存层（Redis） |

---

*最后更新：2025-02*
