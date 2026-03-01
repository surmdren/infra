#!/bin/bash
# ============================================================
# Chatwoot 部署脚本 - 本地 K8s + Cloudflare Tunnel
# 域名: chatwoot.dreamwiseai.com
# NodePort: 30091 → Host: 10008
# ============================================================

set -e

NAMESPACE="chatwoot"
CHART_REPO="https://chatwoot.github.io/charts"
CHART_NAME="chatwoot"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VALUES_FILE="$SCRIPT_DIR/../k8s/chatwoot/values.yaml"
STORAGE_FILE="$SCRIPT_DIR/../k8s/chatwoot/local-storage.yaml"

echo "🚀 开始部署 Chatwoot 到 K8s..."

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
mkdir -p ~/data/chatwoot/postgresql
mkdir -p ~/data/chatwoot/redis
echo "✅ 存储目录创建完成: ~/data/chatwoot/"

# ── 3. 部署本地 StorageClass 和 PV ──────────────────────
echo ""
echo "💾 部署本地存储..."
kubectl apply -f "$STORAGE_FILE"
echo "✅ 存储配置就绪"

# ── 4. 添加 Helm repo ────────────────────────────────────
echo ""
echo "📡 添加 Chatwoot Helm repo..."
helm repo add chatwoot "$CHART_REPO" 2>/dev/null || true
helm repo update
echo "✅ Helm repo 就绪"

# ── 5. 部署 Chatwoot ──────────────────────────────────────
echo ""
echo "⚡ 部署 Chatwoot..."
helm upgrade --install $CHART_NAME chatwoot/$CHART_NAME \
  --namespace $NAMESPACE \
  --values "$VALUES_FILE" \
  --timeout 10m \
  --wait

echo "✅ Chatwoot 部署完成"

# ── 6. 确保 Service 为 NodePort ──────────────────────────
echo ""
echo "🔧 配置 NodePort..."
kubectl patch svc chatwoot -n $NAMESPACE \
  -p '{"spec":{"type":"NodePort","ports":[{"port":80,"targetPort":3000,"nodePort":30091}]}}' \
  2>/dev/null || echo "⚠️  Service 已是 NodePort 或需手动配置"
echo "✅ NodePort 配置完成: 30091 → Host 10008"

# ── 7. 检查状态 ──────────────────────────────────────────
echo ""
echo "🔍 检查部署状态..."
kubectl get pods -n $NAMESPACE
echo ""
kubectl get svc -n $NAMESPACE

# ── 8. 输出访问信息 ──────────────────────────────────────
echo ""
echo "============================================"
echo "✅ Chatwoot 部署完成！"
echo "============================================"
echo ""
echo "📌 本地访问: http://localhost:10008"
echo "📌 Kind 内部: http://172.18.0.2:30091"
echo ""
echo "⚠️  配置 Cloudflare Tunnel 访问:"
echo "   1. 编辑 /etc/cloudflared/config.yml，添加:"
echo ""
echo "   - hostname: chatwoot.dreamwiseai.com"
echo "     service: http://172.18.0.2:30091"
echo ""
echo "   2. 重启 cloudflared:"
echo "      sudo systemctl restart cloudflared"
echo ""
echo "   3. 在 Cloudflare DNS 添加 CNAME 记录:"
echo "      chatwoot.dreamwiseai.com → <tunnel-id>.cfargotunnel.com"
echo ""
echo "📌 公网访问: https://chatwoot.dreamwiseai.com"
echo "============================================"
