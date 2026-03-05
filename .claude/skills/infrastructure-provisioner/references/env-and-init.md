# 环境变量模板 & 初始化脚本

## .env.local 模板

### 模式 A：Supabase + Vercel

```bash
# Schema 命名：取当前目录名，- 转 _，全小写
# PROJECT_SCHEMA=$(basename $(pwd) | tr '[:upper:]' '[:lower:]' | tr '-' '_')

NODE_ENV=development
ENVIRONMENT=local

# 共享凭据（自动从 ~/.dreamai-env 加载）
# NEXT_PUBLIC_SUPABASE_URL     ← 来自 ~/.dreamai-env
# NEXT_PUBLIC_SUPABASE_ANON_KEY ← 来自 ~/.dreamai-env
# SUPABASE_SERVICE_ROLE_KEY    ← 来自 ~/.dreamai-env

# 项目专属
SUPABASE_SCHEMA={project_dir_name}   # e.g., mingkun, ceo_office
NEXTAUTH_SECRET=                     # openssl rand -base64 32

# AI API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Redis（Upstash - Vercel 推荐）
UPSTASH_REDIS_REST_URL=https://xxxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXxx...

# 存储
SUPABASE_STORAGE_BUCKET=myapp-storage
```

### 模式 B：K8s 自托管（PostgreSQL Helm）

```bash
NODE_ENV=development
ENVIRONMENT=local

# PostgreSQL (Local K8s)
POSTGRES_HOST=localhost
POSTGRES_PORT=30432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=devpassword
DATABASE_URL=postgresql://postgres:devpassword@localhost:30432/postgres

# Redis (Local K8s)
REDIS_HOST=localhost
REDIS_PORT=30379
REDIS_URL=redis://localhost:30379

# AWS S3
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET=myapp-local-storage
```

### .env.production 模板

```bash
NODE_ENV=production
ENVIRONMENT=production

POSTGRES_HOST=${RDS_ENDPOINT}
POSTGRES_PORT=5432
POSTGRES_DB=myapp
POSTGRES_USER=admin
POSTGRES_PASSWORD=${DB_PASSWORD}
DATABASE_URL=postgresql://admin:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/myapp

REDIS_HOST=${REDIS_ENDPOINT}
REDIS_PORT=6379
REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_ENDPOINT}:6379

AWS_REGION=${AWS_REGION}
S3_BUCKET=${S3_BUCKET_NAME}
```

---

## scripts/init.sh（Supabase 模式）

> 仅项目首次搭建时执行一次。填写 `.env.local` 后运行。

```bash
#!/usr/bin/env bash
set -euo pipefail

# 加载共享凭据
[ -f "$HOME/.dreamai-env" ] && source "$HOME/.dreamai-env"

# 加载项目专属变量
ENV_FILE="$(dirname "$0")/../.env.local"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

# Step 1: 验证必填变量
REQUIRED=(NEXT_PUBLIC_SUPABASE_URL NEXT_PUBLIC_SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY SUPABASE_SCHEMA)
for VAR in "${REQUIRED[@]}"; do
  [ -z "${!VAR:-}" ] && echo "❌ 缺少 $VAR" && exit 1
done
echo "✅ 环境变量验证通过"

# Step 2: 创建 Supabase Schema
SQL="CREATE SCHEMA IF NOT EXISTS ${SUPABASE_SCHEMA};
GRANT USAGE ON SCHEMA ${SUPABASE_SCHEMA} TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${SUPABASE_SCHEMA} GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${SUPABASE_SCHEMA} GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;"

curl -s -X POST "${NEXT_PUBLIC_SUPABASE_URL}/rest/v1/rpc/exec_sql" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"query\": $(echo "$SQL" | jq -Rs .)}" > /dev/null 2>&1 || true
echo "✅ Schema ${SUPABASE_SCHEMA} 已就绪"
echo "   ⚠️  请到 Supabase → Settings → API → Extra Search Path 添加: ${SUPABASE_SCHEMA}"

# Step 3: 数据库迁移
if command -v npx &>/dev/null && [ -f "prisma/schema.prisma" ]; then
  npx prisma migrate deploy && echo "✅ Prisma 迁移完成"
elif command -v npx &>/dev/null && [ -f "drizzle.config.ts" ]; then
  npx drizzle-kit migrate && echo "✅ Drizzle 迁移完成"
else
  echo "ℹ️  未检测到 Prisma/Drizzle，跳过迁移"
fi

# Step 4: 验证连接
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "${NEXT_PUBLIC_SUPABASE_URL}/rest/v1/" \
  -H "apikey: ${NEXT_PUBLIC_SUPABASE_ANON_KEY}")
[ "$HTTP_STATUS" = "200" ] && echo "✅ Supabase 连接正常" || { echo "❌ 连接失败 (HTTP $HTTP_STATUS)"; exit 1; }

echo "✅ 项目初始化完成！运行 npm run dev 启动。"
```
