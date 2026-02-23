# DreamAI Platform Infrastructure

自托管的共享基础设施，支撑所有 DreamAI 旗下项目。

## 核心能力

| 能力 | 技术 | 用途 |
|------|------|------|
| 数据库 | PostgreSQL + pgvector | 业务数据 + AI 向量检索 |
| 认证 | Supabase Auth (GoTrue) | 用户登录/注册/JWT |
| 文件存储 | MinIO (S3 兼容) | 图片、视频、文件 |
| REST API | PostgREST | 自动生成 CRUD API |
| Realtime | Supabase Realtime | WebSocket 实时推送 |
| Edge Functions | Deno Runtime | Serverless 函数 |

## 支撑的项目

- `ai-cofounder` — AI 创业验证助手
- `chatseo` — AI 出海 SEO 工具
- `sleek-design` — AI UI 生成工具
- `appforge` — 小程序生成平台
- `growth-engine` — 内容增长工具
- 更多项目持续接入...

## 快速开始

```bash
# 1. 克隆并配置环境变量
git clone https://github.com/surmdren/infra
cd infra
cp supabase/.env.example supabase/.env
# 编辑 .env 填入你的密钥

# 2. Docker Compose 启动（开发/测试）
cd supabase
docker compose up -d

# 3. K8s 部署（生产）
kubectl apply -f k8s/
```

## 目录结构

```
infra/
├── supabase/              # Supabase 自托管配置
│   ├── docker-compose.yml
│   ├── .env.example
│   └── config/
│       └── kong.yml       # API Gateway 路由配置
├── k8s/                   # Kubernetes 生产配置
│   ├── supabase/          # Supabase 相关 manifests
│   ├── monitoring/        # Prometheus + Grafana
│   └── ingress/           # Nginx Ingress 配置
├── scripts/               # 运维脚本
│   ├── backup.sh          # 数据库备份
│   ├── restore.sh         # 数据库恢复
│   └── new-project.sh     # 新建项目 schema
└── docs/                  # 文档
    ├── architecture.md    # 架构说明
    ├── onboarding.md      # 新项目接入指南
    └── operations.md      # 运维手册
```

## 多项目隔离方案

每个项目使用独立的 PostgreSQL schema + Supabase Project，共享底层数据库实例：

```
PostgreSQL Instance
├── schema: aicofounder     # ai-cofounder 项目专用
├── schema: chatseo         # chatseo 项目专用
├── schema: sleekdesign     # sleek-design 项目专用
└── schema: public          # 共享数据（用户跨产品 SSO）
```

## 路线图

详见 [docs/roadmap.md](docs/roadmap.md)

**Phase 1** ✅ 基础能力（数据库/认证/存储/Realtime）  
**Phase 2** 🔜 支付 + 邮件 + 任务队列  
**Phase 3** 🔜 LiteLLM AI代理 + GPU 调度  
**Phase 4** 🔜 Prometheus + Grafana 可观测性  

## 项目接入

新项目接入只需 3 步：

```bash
# 1. 创建项目 schema
./scripts/new-project.sh <project-name>

# 2. 获取项目连接参数
./scripts/get-credentials.sh <project-name>

# 3. 在项目中配置环境变量
SUPABASE_URL=http://your-server:8000
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx
```
