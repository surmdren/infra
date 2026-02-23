# DreamAI Platform - 架构说明

## 总体架构

```
                    ┌─────────────────────────────┐
                    │     DreamAI Projects         │
                    │  aicofounder / chatseo /      │
                    │  sleek-design / appforge ...  │
                    └──────────────┬──────────────┘
                                   │ HTTP / SDK
                    ┌──────────────▼──────────────┐
                    │         Kong (Port 8000)      │
                    │         API Gateway           │
                    └──┬────┬────┬────┬────────────┘
                       │    │    │    │
           ┌───────────▼┐  ┌▼──┐ ┌▼──┐ ┌▼──────────┐
           │ PostgREST  │  │Auth│ │Real│ │  Storage  │
           │ REST API   │  │GoT │ │time│ │  MinIO    │
           └─────┬──────┘  └─┬─┘ └─┬─┘ └──────┬────┘
                 │            │     │            │
                 └────────────▼─────▼────────────┘
                         ┌──────────┐
                         │PostgreSQL│
                         │  + pgvector
                         └──────────┘
```

## 多项目 Schema 隔离

```
PostgreSQL Database: postgres
├── schema: public          # 共享数据（跨产品 SSO）
├── schema: auth            # Supabase Auth 系统表
├── schema: storage         # 文件存储元数据
├── schema: aicofounder     # ai-cofounder 项目数据
├── schema: chatseo         # chatseo 项目数据
├── schema: sleekdesign     # sleek-design 项目数据
├── schema: appforge        # appforge 项目数据
└── schema: growthengine    # growth-engine 项目数据
```

## 网络端口

| 端口 | 服务 | 说明 |
|------|------|------|
| 8000 | Kong | API 统一入口（生产环境用 Nginx 反代）|
| 3000 | Studio | Web 管理界面 |
| 5432 | PostgreSQL | 数据库（内部访问）|
| 9999 | GoTrue | Auth 服务（内部）|
| 4000 | Realtime | WebSocket（通过 Kong 暴露）|

## 生产部署（K8s）

所有服务部署在 K8s namespace `platform` 下：

```
namespace: platform
├── deployment: supabase-kong
├── deployment: supabase-auth
├── deployment: supabase-rest
├── deployment: supabase-realtime
├── deployment: supabase-storage
├── statefulset: postgres
├── service: kong (NodePort/LoadBalancer)
└── ingress: platform-ingress
```

## 成本估算

| 规模 | 服务器配置 | 月成本 |
|------|-----------|--------|
| 0-10 用户/项目 | 2C4G 单节点 | ~¥100/月 |
| 10-1000 用户/项目 | 4C8G | ~¥300/月 |
| 1000+ 用户/项目 | K8s 多节点 | ~¥800/月 |

对比 Supabase Cloud Pro（$25/项目/月），5个项目 = $125/月 ≈ ¥900/月
**自托管可节省 60-90%**
