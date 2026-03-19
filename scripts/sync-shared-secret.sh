#!/bin/bash
# ============================================================
# 同步共享 Secret 到所有 SaaS 命名空间
# 用法:
#   ./scripts/sync-shared-secret.sh dev    # 同步 dev 环境
#   ./scripts/sync-shared-secret.sh prod   # 同步 prod 环境
# ============================================================

set -e

ENV=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../envs/${ENV}.env"
SECRET_NAME="dreamai-shared"

# 验证环境文件存在
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ 找不到环境文件: $ENV_FILE"
  exit 1
fi

# 根据环境选择 kubeconfig
if [ "$ENV" = "prod" ]; then
  export KUBECONFIG=~/.kube/prod.yaml
else
  export KUBECONFIG=~/.kube/k3s.yaml
fi

echo "🌍 环境: $ENV"
echo "📋 配置文件: $ENV_FILE"
echo "☸️  集群: $(kubectl config current-context)"
echo ""

# 获取所有 SaaS 命名空间（排除系统 namespace）
NAMESPACES=$(kubectl get namespaces --no-headers \
  | awk '{print $1}' \
  | grep -v "^kube-\|^local-path\|^default$")

echo "📦 将同步到以下 namespace:"
echo "$NAMESPACES" | sed 's/^/   - /'
echo ""

# 为每个 namespace 创建/更新 Secret
for NS in $NAMESPACES; do
  kubectl create secret generic $SECRET_NAME \
    --from-env-file="$ENV_FILE" \
    --namespace="$NS" \
    --dry-run=client -o yaml \
    | kubectl apply -f - > /dev/null 2>&1
  echo "✅ $NS"
done

echo ""
echo "🎉 完成！所有 namespace 的 '$SECRET_NAME' Secret 已更新"
echo ""
echo "📖 在 Deployment 中引用方式:"
echo ""
echo "   envFrom:"
echo "     - secretRef:"
echo "         name: $SECRET_NAME"
echo "   env:"
echo "     # 项目专属变量仍在自己的 Secret 里"
echo "     - name: SUPABASE_SCHEMA"
echo "       value: my-project"
