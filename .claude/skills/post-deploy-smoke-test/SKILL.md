---
name: post-deploy-smoke-test
description: 部署完成后的冒烟测试。验证 K8s Pod 健康状态、核心 API 端点可用性、前端页面可访问性。输出报告到 QA/smoke-test-report.md。应在 dev-deploy 完成后立即执行。当用户提到"部署后测试"、"冒烟测试"、"smoke test"、"post-deploy"、"验证部署"、"部署验证"时触发。
---

# 部署后冒烟测试

## Overview

```
1. K8s 健康检查（Pod / Deployment / Service 状态）
2. API 端点探测（core endpoints 真实请求）
3. 前端页面可访问性验证
4. 生成报告 → QA/smoke-test-report.md
```

> ⚠️ 所有测试调用真实部署环境，禁止 Mock。

---

## 前置条件

```bash
# 读取部署环境变量
source ~/.dreamai-env 2>/dev/null
source .env.local 2>/dev/null || source .env 2>/dev/null

export PROJECT=${PROJECT:-$(basename $(pwd))}
export ENV=${ENV:-prod}
export DOMAIN=${DOMAIN:-localhost}

# k3s 环境
if [ "${CLUSTER_TYPE}" = "k3s" ]; then
  export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
fi
```

---

## Step 1: K8s 集群健康检查

```bash
echo "=== Pod 状态 ==="
kubectl get pods --all-namespaces -l app=${PROJECT},env=${ENV}

echo "=== Deployment 状态 ==="
kubectl get deployments -n ${PROJECT}-${ENV}-backend
kubectl get deployments -n ${PROJECT}-${ENV}-frontend

echo "=== 检查 Pod 是否全部 Running ==="
FAILED_PODS=$(kubectl get pods --all-namespaces -l app=${PROJECT},env=${ENV} \
  --field-selector=status.phase!=Running \
  --no-headers 2>/dev/null | wc -l)

if [ "$FAILED_PODS" -gt 0 ]; then
  echo "❌ 发现 $FAILED_PODS 个异常 Pod"
  kubectl get pods --all-namespaces -l app=${PROJECT},env=${ENV} \
    --field-selector=status.phase!=Running
  kubectl describe pods --all-namespaces -l app=${PROJECT},env=${ENV} \
    --field-selector=status.phase!=Running
else
  echo "✅ 所有 Pod 状态正常"
fi

echo "=== 资源使用 ==="
kubectl top pods -n ${PROJECT}-${ENV}-backend 2>/dev/null || echo "(metrics-server 未安装，跳过)"
```

---

## Step 2: API 端点探测

**读取项目 API 列表**（优先从 `api-docs/` 或 `TechSolution/` 读取核心端点，否则测试默认端点）：

```bash
BASE_URL="https://${DOMAIN}"
PASS=0
FAIL=0
RESULTS=""

check_endpoint() {
  local method=$1
  local path=$2
  local expected_status=$3
  local description=$4

  actual_status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X ${method} "${BASE_URL}${path}" \
    -H "Content-Type: application/json" \
    --max-time 10 2>/dev/null)

  if [ "$actual_status" = "$expected_status" ]; then
    echo "✅ ${method} ${path} → ${actual_status} (${description})"
    RESULTS="${RESULTS}\n| ✅ | ${method} | \`${path}\` | ${expected_status} | ${actual_status} | ${description} |"
    PASS=$((PASS + 1))
  else
    echo "❌ ${method} ${path} → ${actual_status} (期望 ${expected_status}) (${description})"
    RESULTS="${RESULTS}\n| ❌ | ${method} | \`${path}\` | ${expected_status} | ${actual_status} | ${description} |"
    FAIL=$((FAIL + 1))
  fi
}

# 核心健康端点（必测）
check_endpoint "GET" "/api/health"  "200" "Backend 健康检查"
check_endpoint "GET" "/api/ready"   "200" "Backend 就绪检查"

# 从项目代码自动扫描并测试核心 API（认证类返回 401 视为正常）
# Claude 需读取 app/api/ 或 src/routes/ 目录，提取无需 auth 的 GET 端点
# 对需要 auth 的端点，期望状态改为 401
check_endpoint "GET" "/api/version" "200" "版本信息"
```

---

## Step 3: 前端页面可访问性

```bash
echo "=== 前端页面检查 ==="

check_page() {
  local path=$1
  local description=$2

  status=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://${DOMAIN}${path}" --max-time 15 2>/dev/null)
  size=$(curl -s "https://${DOMAIN}${path}" --max-time 15 2>/dev/null | wc -c)

  if [ "$status" = "200" ] && [ "$size" -gt 100 ]; then
    echo "✅ ${path} → ${status} (${size} bytes) (${description})"
    PAGE_RESULTS="${PAGE_RESULTS}\n| ✅ | \`${path}\` | ${status} | ${size} bytes | ${description} |"
    PASS=$((PASS + 1))
  else
    echo "❌ ${path} → ${status} (${size} bytes) (${description})"
    PAGE_RESULTS="${PAGE_RESULTS}\n| ❌ | \`${path}\` | ${status} | ${size} bytes | ${description} |"
    FAIL=$((FAIL + 1))
  fi
}

check_page "/" "首页"
check_page "/login" "登录页"

# Claude 从项目 app/ 目录扫描其他核心页面路由并测试
```

---

## Step 4: 生成报告

```bash
mkdir -p QA
REPORT_FILE="QA/smoke-test-report.md"
TOTAL=$((PASS + FAIL))
STATUS_ICON=$([ "$FAIL" -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")

cat > "$REPORT_FILE" << EOF
# 部署后冒烟测试报告

**状态**: ${STATUS_ICON}
**环境**: ${ENV} | **域名**: ${DOMAIN} | **时间**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**结果**: ${PASS}/${TOTAL} 通过，${FAIL} 失败

---

## K8s 集群状态

\`\`\`
$(kubectl get pods --all-namespaces -l app=${PROJECT},env=${ENV} 2>/dev/null)
\`\`\`

---

## API 端点测试

| 状态 | 方法 | 路径 | 期望 | 实际 | 说明 |
|------|------|------|------|------|------|
$(echo -e "$RESULTS")

---

## 前端页面测试

| 状态 | 路径 | HTTP | 大小 | 说明 |
|------|------|------|------|------|
$(echo -e "$PAGE_RESULTS")

---

## $([ "$FAIL" -eq 0 ] && echo "结论：部署验证通过，服务运行正常。" || echo "结论：发现 ${FAIL} 个问题，需立即处理。请检查上方失败项，必要时执行回滚：")
$([ "$FAIL" -gt 0 ] && echo "\`\`\`bash
kubectl rollout undo deployment/backend -n ${PROJECT}-${ENV}-backend
kubectl rollout undo deployment/frontend -n ${PROJECT}-${ENV}-frontend
\`\`\`")
EOF

echo ""
echo "报告已保存: ${REPORT_FILE}"
echo "总计: ${PASS}/${TOTAL} 通过"

# 失败时以非零退出码退出，方便 CI/CD 检测
[ "$FAIL" -gt 0 ] && exit 1 || exit 0
```

---

## 注意事项

1. **执行时机**：在 `dev-deploy` 完成后立即执行
2. **失败处理**：有任何失败项时，立即参考报告中的回滚命令
3. **CI/CD 集成**：脚本以非零退出码退出，可直接接入 pipeline 的失败检测
4. **端点扫描**：Claude 会自动读取项目的路由文件（`app/api/`、`src/routes/`）提取真实端点，不依赖硬编码列表
