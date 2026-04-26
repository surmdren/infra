#!/usr/bin/env bash
# 从 .env.local（app keys）+ dev.env（Supabase）创建 K8s secret
# 用法：bash create-secrets.sh
set -euo pipefail

APP_ENV="/home/ysurmd/github/dreamai/ai-cofounder/app/.env.local"
DEV_ENV="/home/ysurmd/github/dreamai/infra/envs/dev.env"

get() { grep "^$1=" "$2" 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'"; }

export KUBECONFIG=~/.kube/k3s.yaml

kubectl create secret generic aicofounder-secrets \
  --namespace aicofounder-dev \
  --from-literal=supabase-url="$(get SUPABASE_URL $DEV_ENV)" \
  --from-literal=supabase-anon-key="$(get SUPABASE_ANON_KEY $DEV_ENV)" \
  --from-literal=supabase-service-role-key="$(get SUPABASE_SERVICE_ROLE_KEY $DEV_ENV)" \
  --from-literal=zhipu-api-key="$(get ZHIPU_API_KEY $APP_ENV)" \
  --from-literal=deepseek-api-key="$(get DEEPSEEK_API_KEY $APP_ENV)" \
  --from-literal=ai-model="$(get AI_MODEL $APP_ENV)" \
  --from-literal=brave-search-api-key="$(get BRAVE_SEARCH_API_KEY $APP_ENV)" \
  --from-literal=github-client-id="$(get GITHUB_CLIENT_ID $APP_ENV)" \
  --from-literal=github-client-secret="$(get GITHUB_CLIENT_SECRET $APP_ENV)" \
  --from-literal=google-client-id="$(get GOOGLE_CLIENT_ID $APP_ENV)" \
  --from-literal=google-client-secret="$(get GOOGLE_CLIENT_SECRET $APP_ENV)" \
  --from-literal=wechat-app-id="$(get NEXT_PUBLIC_WECHAT_APP_ID $APP_ENV)" \
  --from-literal=wechat-mch-id="$(get WECHAT_MCH_ID $APP_ENV)" \
  --from-literal=wechat-api-v3-key="$(get WECHAT_API_V3_KEY $APP_ENV)" \
  --from-literal=wechat-private-key="$(get WECHAT_PRIVATE_KEY $APP_ENV)" \
  --from-literal=wechat-serial-no="$(get WECHAT_SERIAL_NO $APP_ENV)" \
  --from-literal=paypal-client-id="$(get PAYPAL_CLIENT_ID $APP_ENV)" \
  --from-literal=paypal-client-secret="$(get PAYPAL_CLIENT_SECRET $APP_ENV)" \
  --from-literal=posthog-key="$(get NEXT_PUBLIC_POSTHOG_KEY $APP_ENV)" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ aicofounder-secrets created/updated"
