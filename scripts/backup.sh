#!/bin/bash
# 数据库备份脚本，建议通过 cron 每日执行
# 使用方法: ./scripts/backup.sh [project-name|all]

set -e

source ./supabase/.env

BACKUP_DIR="./backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

PROJECT=${1:-all}

do_backup() {
  local schema=$1
  echo "📦 备份 schema: $schema"
  pg_dump \
    "postgres://postgres:${POSTGRES_PASSWORD}@localhost:5432/postgres" \
    --schema="$schema" \
    --no-owner \
    --no-acl \
    -f "$BACKUP_DIR/${schema}_$(date +%H%M%S).sql"
  gzip "$BACKUP_DIR/${schema}_$(date +%H%M%S).sql" 2>/dev/null || true
  echo "✅ 备份完成: $BACKUP_DIR/$schema*.sql"
}

if [ "$PROJECT" = "all" ]; then
  # 备份所有非系统 schema
  schemas=$(psql "postgres://postgres:${POSTGRES_PASSWORD}@localhost:5432/postgres" \
    -t -c "SELECT schema_name FROM information_schema.schemata
           WHERE schema_name NOT IN ('information_schema','pg_catalog','pg_toast')
           AND schema_name NOT LIKE 'pg_%';")
  for schema in $schemas; do
    do_backup "$schema"
  done
else
  do_backup "$PROJECT"
fi

echo ""
echo "🎉 备份完成，保存在: $BACKUP_DIR"

# 清理 30 天前的备份
find ./backups -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
