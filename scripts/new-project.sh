#!/bin/bash
# 新建项目 schema，为每个新项目初始化隔离的数据库空间
# 使用方法: ./scripts/new-project.sh <project-name>

set -e

PROJECT=$1
if [ -z "$PROJECT" ]; then
  echo "Usage: $0 <project-name>"
  echo "Example: $0 aicofounder"
  exit 1
fi

source ./supabase/.env

echo "🚀 初始化项目 schema: $PROJECT"

# 在 PostgreSQL 中创建独立 schema
psql "postgres://postgres:${POSTGRES_PASSWORD}@localhost:5432/postgres" << SQL
-- 创建项目专属 schema
CREATE SCHEMA IF NOT EXISTS ${PROJECT};

-- 创建专属角色
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${PROJECT}_owner') THEN
    CREATE ROLE ${PROJECT}_owner;
  END IF;
END
\$\$;

-- 授权
GRANT ALL ON SCHEMA ${PROJECT} TO ${PROJECT}_owner;
GRANT USAGE ON SCHEMA ${PROJECT} TO anon, authenticated, service_role;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA ${PROJECT}
  GRANT ALL ON TABLES TO ${PROJECT}_owner;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${PROJECT}
  GRANT SELECT ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA ${PROJECT}
  GRANT ALL ON TABLES TO authenticated;

SELECT 'Schema ${PROJECT} created successfully' as result;
SQL

echo ""
echo "✅ 项目 schema 创建完成: $PROJECT"
echo ""
echo "📋 项目连接配置："
echo "   SUPABASE_URL=http://localhost:8000"
echo "   SUPABASE_ANON_KEY=${ANON_KEY}"
echo "   SUPABASE_SERVICE_KEY=${SERVICE_ROLE_KEY}"
echo "   DB_SCHEMA=${PROJECT}"
echo ""
echo "📁 建议在项目根目录创建 .env 文件并填入以上配置"
