#!/bin/bash
# 重新生成 Supabase 所有密钥
# 使用场景：首次部署或密钥泄露需要轮换

set -e

OUTPUT_FILE="$(dirname "$0")/../k8s/supabase/secrets.env"

echo "🔐 生成 Supabase 密钥..."

JWT_SECRET=$(openssl rand -base64 40 | tr -d '\n/+=' | head -c 40)
DB_PASSWORD=$(openssl rand -base64 24 | tr -d '\n/+=' | head -c 24)
REALTIME_SECRET=$(openssl rand -base64 64 | tr -d '\n')
CRYPTO_KEY=$(openssl rand -hex 16)
S3_KEY_ID=$(openssl rand -hex 16)
S3_ACCESS_KEY=$(openssl rand -hex 32)
LOGFLARE_PUBLIC=$(openssl rand -base64 24 | tr -d '\n/+=')
LOGFLARE_PRIVATE=$(openssl rand -base64 24 | tr -d '\n/+=')
DASHBOARD_PASS=$(openssl rand -base64 12 | tr -d '\n/+=')
MINIO_PASS=$(openssl rand -base64 12 | tr -d '\n/+=')

ANON_JWT=$(python3 -c "
import json, base64, hmac, hashlib
secret = '${JWT_SECRET}'
header = base64.urlsafe_b64encode(json.dumps({'alg':'HS256','typ':'JWT'}).encode()).rstrip(b'=').decode()
payload = base64.urlsafe_b64encode(json.dumps({'role':'anon','iss':'supabase','iat':1641769200,'exp':1999999999}).encode()).rstrip(b'=').decode()
sig = base64.urlsafe_b64encode(hmac.new(secret.encode(), f'{header}.{payload}'.encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
print(f'{header}.{payload}.{sig}')
")

SERVICE_JWT=$(python3 -c "
import json, base64, hmac, hashlib
secret = '${JWT_SECRET}'
header = base64.urlsafe_b64encode(json.dumps({'alg':'HS256','typ':'JWT'}).encode()).rstrip(b'=').decode()
payload = base64.urlsafe_b64encode(json.dumps({'role':'service_role','iss':'supabase','iat':1641769200,'exp':1999999999}).encode()).rstrip(b'=').decode()
sig = base64.urlsafe_b64encode(hmac.new(secret.encode(), f'{header}.{payload}'.encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
print(f'{header}.{payload}.{sig}')
")

cat > "$OUTPUT_FILE" << EOF
# ⚠️  此文件包含真实密钥，已加入 .gitignore，不会提交到 git
# 生成时间: $(date)

JWT_SECRET=${JWT_SECRET}
DB_PASSWORD=${DB_PASSWORD}
ANON_JWT=${ANON_JWT}
SERVICE_JWT=${SERVICE_JWT}
REALTIME_SECRET=${REALTIME_SECRET}
CRYPTO_KEY=${CRYPTO_KEY}
S3_KEY_ID=${S3_KEY_ID}
S3_ACCESS_KEY=${S3_ACCESS_KEY}
LOGFLARE_PUBLIC=${LOGFLARE_PUBLIC}
LOGFLARE_PRIVATE=${LOGFLARE_PRIVATE}
DASHBOARD_USERNAME=supabase
DASHBOARD_PASSWORD=${DASHBOARD_PASS}
MINIO_USER=supa-storage
MINIO_PASSWORD=${MINIO_PASS}
EOF

echo "✅ 密钥已保存到: $OUTPUT_FILE"
echo ""
echo "⚠️  请同步更新 k8s/supabase/values.yaml 中对应的密钥值"
