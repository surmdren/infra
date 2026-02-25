#!/bin/bash
# ============================================================
# Supabase 部署脚本 - 本地 K8s + Cloudflare Tunnel
# 域名: supabase.dreamwiseai.com
# ============================================================

set -e

NAMESPACE="supabase"
CHART_REPO="https://supabase-community.github.io/supabase-kubernetes"
CHART_NAME="supabase"
VALUES_FILE="$(dirname "$0")/../k8s/supabase/values.yaml"
STORAGE_FILE="$(dirname "$0")/../k8s/supabase/local-storage.yaml"
INGRESS_FILE="$(dirname "$0")/../k8s/supabase/ingress.yaml"

echo "🚀 开始部署 Supabase 到 K8s..."

# ── 0. 前置检查 ──────────────────────────────────────────
echo ""
echo "📋 检查依赖工具..."
for tool in kubectl helm; do
  if ! command -v $tool &> /dev/null; then
    echo "❌ 未找到 $tool，请先安装"
    exit 1
  fi
done
echo "✅ 工具检查通过"

# ── 1. 创建 namespace ────────────────────────────────────
echo ""
echo "📦 创建 namespace: $NAMESPACE"
kubectl get namespace $NAMESPACE &>/dev/null || kubectl create namespace $NAMESPACE
echo "✅ Namespace 就绪"

# ── 2. 创建本地存储目录 ──────────────────────────────────
echo ""
echo "💾 创建本地存储目录..."
sudo mkdir -p /data/supabase/db
sudo mkdir -p /data/supabase/storage
sudo mkdir -p /data/supabase/minio
sudo chmod -R 777 /data/supabase
echo "✅ 存储目录创建完成"

# ── 3. 部署本地 StorageClass 和 PV ──────────────────────
echo ""
echo "💾 部署本地存储..."
kubectl apply -f "$STORAGE_FILE"
echo "✅ 存储配置就绪"

# ── 4. 添加 Helm repo ────────────────────────────────────
echo ""
echo "📡 添加 Supabase Helm repo..."
helm repo add supabase "$CHART_REPO" 2>/dev/null || true
helm repo update
echo "✅ Helm repo 就绪"

# ── 5. 跳过 nginx-ingress（使用 NodePort 方式）──────────
echo ""
echo "🌐 使用 NodePort 方式暴露服务，无需 nginx-ingress"
echo "   Kong API:  http://localhost:30800"
echo "   Studio UI: http://localhost:30300"

# ── 6. 部署 Supabase ────────────────────────────────────
echo ""
echo "⚡ 部署 Supabase..."
helm upgrade --install $CHART_NAME supabase/$CHART_NAME \
  --namespace $NAMESPACE \
  --values "$VALUES_FILE" \
  --timeout 10m \
  --wait

echo "✅ Supabase 部署完成"

# ── 7. 部署 Ingress 和 Cloudflare Tunnel ───────────────
echo ""
echo "🌐 部署 Ingress..."
kubectl apply -f "$INGRESS_FILE" -n $NAMESPACE
echo "✅ Ingress 配置完成"

# ── 8. 检查状态 ──────────────────────────────────────────
echo ""
echo "🔍 检查部署状态..."
kubectl get pods -n $NAMESPACE
echo ""
kubectl get svc -n $NAMESPACE
echo ""
kubectl get ingress -n $NAMESPACE

# ── 9. 提醒填写 Cloudflare Token ────────────────────────
echo ""
echo "============================================"
echo "⚠️  重要：填写 Cloudflare Tunnel Token"
echo "============================================"
echo ""
echo "1. 登录 Cloudflare Dashboard → Zero Trust → Tunnels"
echo "2. 创建 Tunnel，名称: dreamai-local"
echo "3. 复制 Token"
echo "4. 执行以下命令填入 Token:"
echo ""
echo "   kubectl create secret generic cloudflared-secret \\"
echo "     --from-literal=token=YOUR_TOKEN \\"
echo "     --namespace=$NAMESPACE \\"
echo "     --dry-run=client -o yaml | kubectl apply -f -"
echo ""
echo "5. Tunnel 配置 Public Hostname:"
echo "   Domain: supabase.dreamwiseai.com"
echo "   Service: http://ingress-nginx-controller.ingress-nginx:80"
echo ""
echo "============================================"
echo "✅ 部署完成！访问: https://supabase.dreamwiseai.com"
echo "============================================"
