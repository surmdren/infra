---
name: dev-deploy
description: 将应用部署到Kubernetes集群。构建容器镜像、推送到镜像仓库、更新K8s配置、执行数据库迁移、验证部署状态、回滚支持。本地测试环境使用 kind 集群；轻量生产/自托管环境使用 k3s（内置 Traefik Ingress + ServiceLB）；云端生产环境适用于AWS EKS、阿里云ACK。支持多环境部署（dev/staging/prod）。当用户提到"部署"、"发布"、"上线"、"deploy"、"K8s部署"、"k3s"时触发。
---

# Kubernetes 部署执行器

## Overview

```
1. 部署前检查（前置条件 + Namespace 规范）
2. 构建容器镜像（Docker Build）
3. 推送镜像仓库（ECR/ACR）
4. 更新 K8s 配置（Deployment / Service / Ingress）
5. 执行数据库迁移（Migration Job）
6. 滚动更新监控（rollout status）
7. 验证部署 + 生成报告
```

## Namespace 命名规范

```
main 分支部署:       <project>-<component>            # 快速部署，无 env 后缀
staging（tag 触发）: <project>-staging-<component>
prod（tag + 审批）:  <project>-prod-<component>
dev（本地 kind）:    <project>-dev-<component>

示例:
  myapp-backend            # main 分支部署
  myapp-staging-backend    # staging
  myapp-prod-backend       # prod
  myapp-dev-backend        # 本地 kind 测试
```

| 环境 | Namespace 格式 | 触发方式 | 资源规格 |
|------|---------------|---------|---------|
| dev | `<project>-dev-<component>` | 其他分支，kind 集群 | 低配置 |
| main | `<project>-<component>` | main 分支推送 | 中等配置 |
| staging | `<project>-staging-<component>` | 打 tag `v*.*.*` | 中等配置 |
| prod | `<project>-prod-<component>` | tag + 手动审批 | 高配置 + HPA |

> **强制规则：创建 Namespace 时必须同步创建 ResourceQuota + LimitRange。**

```bash
# prod namespace（无 env 后缀）
kubectl create namespace ${PROJECT}-backend
# staging namespace
kubectl create namespace ${PROJECT}-staging-backend
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota
  namespace: ${NAMESPACE}   # prod: ${PROJECT}-backend  staging: ${PROJECT}-staging-backend
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 2Gi
    limits.cpu: "2"
    limits.memory: 4Gi
    pods: "10"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: limits
  namespace: ${NAMESPACE}
spec:
  limits:
    - type: Container
      default: { cpu: "500m", memory: "512Mi" }
      defaultRequest: { cpu: "100m", memory: "128Mi" }
EOF
```

---

## 集群类型选择

| 集群 | 适用场景 | Ingress | 镜像加载 |
|------|---------|---------|---------|
| **kind** | 本地开发测试 | 需手动安装 | `kind load docker-image` |
| **k3s** ⭐ 默认 | 轻量生产 / 自托管 / 边缘 | **Traefik（内置，默认）** | push 到 registry 或 `k3s ctr images import` |
| **AWS EKS** | 云端生产 | AWS ALB | push 到 ECR |
| **阿里云 ACK** | 云端生产 | ALB/Nginx | push 到 ACR |

> **默认 Ingress Controller：Traefik**（k3s 内置，无需额外安装）。仅在 AWS EKS 时切换为 ALB。

---

## Step 1: 部署前检查

```bash
# 自动推导项目名（与 infrastructure-provisioner 和 Supabase schema 命名逻辑一致）
export PROJECT=$(basename $(pwd) | tr '[:upper:]' '[:lower:]' | tr '-' '_')
echo "Project: $PROJECT"

cat TechSolution/infrastructure/kubernetes.md
cat DevPlan/checklist.md
# 确认：Dockerfile 存在 / K8s 配置文件存在 / kubectl 已配置 / 镜像仓库权限

# k3s 环境额外检查
if [ "${CLUSTER_TYPE}" = "k3s" ]; then
  export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
  kubectl get nodes  # 确认 k3s 集群正常
fi
```

---

## Step 1.5: 确定部署版本号和 Namespace

部署脚本**不创建 git tag**。Tag 由开发者手动打，或由 CI 在 push tag 时自动触发。

```bash
# 自动检测当前环境（根据分支名）
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ -z "${ENV}" ]; then
  case "${CURRENT_BRANCH}" in
    main) export ENV="main" ;;
    staging) export ENV="staging" ;;
    *)  export ENV="dev" ;;
  esac
fi

# Namespace 生成函数（ENV 决定前缀，component 由调用方传入）
# main → <project>-<component>（无 env 后缀）
# staging → <project>-staging-<component>
# dev → <project>-dev-<component>
ns() {
  local component=$1
  case "${ENV}" in
    main)    echo "${PROJECT}-${component}" ;;
    staging) echo "${PROJECT}-staging-${component}" ;;
    prod)    echo "${PROJECT}-prod-${component}" ;;
    dev)     echo "${PROJECT}-dev-${component}" ;;
  esac
}
# 示例：ns backend → myapp-backend（main）或 myapp-staging-backend（staging）

# 确定镜像版本号
case "${ENV}" in
  dev)
    # 本地 kind 集群：先确保所有改动已 commit，再用 commit hash 作为镜像 tag
    # 保证镜像内容与 tag 完全对应，避免调试时出现「代码和 tag 不一致」的问题
    if ! git diff --quiet || ! git diff --cached --quiet; then
      echo "⚠️  有未提交的改动，请先 commit 再部署（可用 wip: 前缀）"
      echo "   git add . && git commit -m 'wip: <描述>'"
      exit 1
    fi
    export VERSION=$(git rev-parse --short HEAD)
    echo "🔧 本地开发部署 | ENV=dev | VERSION=${VERSION}"
    ;;
  main)
    # main 分支直接部署，使用 commit hash
    if ! git diff --quiet || ! git diff --cached --quiet; then
      echo "⚠️  有未提交的改动，请先 commit 再部署"
      exit 1
    fi
    export VERSION=$(git rev-parse --short HEAD)
    echo "🚀 main 部署（无环境区分）| VERSION=${VERSION}"
    ;;
  staging)
    # staging：由 CI 在 push v*.*.* tag 时触发，使用语义化 tag
    export VERSION=$(git describe --tags --always)
    if [[ "${VERSION}" != v*.*.* ]]; then
      echo "⚠️  当前 HEAD 无语义化 tag（如 v1.2.0），VERSION 将为 ${VERSION}"
      echo "   staging 部署建议先打 tag：git tag v1.2.0 && git push origin v1.2.0"
    fi
    echo "🧪 staging 部署 | VERSION=${VERSION}"
    ;;
esac
```

> **部署策略：**
> - `main` 分支：直接部署到 `<project>-<component>`（无 env 后缀），commit hash 作为版本号
> - `v*.*.*` tag：先自动部署到 staging（`<project>-staging-<component>`），手动审批后同一 tag 部署到 prod（`<project>-prod-<component>`）
> - `dev`（本地 kind）：commit hash 作为镜像 tag，不推送 registry
> - `latest` / `staging-latest`：仅作为 Docker Build Cache，**不用于部署引用**

---

## Step 2: 构建容器镜像

**Backend Dockerfile**（多阶段构建 + 非 root 用户）：
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

**Frontend Dockerfile**：
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
VERSION=$(git describe --tags --always)
docker build -t backend:${VERSION} -f backend/Dockerfile .
docker build -t frontend:${VERSION} -f frontend/Dockerfile .
```

---

## Step 3: 推送镜像仓库

**本地 kind 集群**（直接加载到 kind，无需 registry）：
```bash
kind load docker-image backend:${VERSION} --name ${KIND_CLUSTER_NAME:-kind}
kind load docker-image frontend:${VERSION} --name ${KIND_CLUSTER_NAME:-kind}
```

**k3s**（两种方式二选一）：
```bash
# 方式 A：导入本地镜像（无 registry 时）
docker save backend:${VERSION} | sudo k3s ctr images import -
docker save frontend:${VERSION} | sudo k3s ctr images import -

# 方式 B：push 到 registry，k3s 自动 pull（推荐）
docker tag backend:${VERSION} ${REGISTRY}/backend:${VERSION}
docker push ${REGISTRY}/backend:${VERSION}
# 若使用私有 registry，需配置 /etc/rancher/k3s/registries.yaml
```

**AWS ECR**（生产环境）：
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ${ECR_REGISTRY}
docker tag backend:${VERSION} ${ECR_REGISTRY}/myapp/backend:${VERSION}
docker push ${ECR_REGISTRY}/myapp/backend:${VERSION}
```

**阿里云 ACR**（生产环境）：
```bash
docker login --username=xxx@aliyun.com registry.cn-hangzhou.aliyuncs.com
docker tag backend:${VERSION} registry.cn-hangzhou.aliyuncs.com/myapp/backend:${VERSION}
docker push registry.cn-hangzhou.aliyuncs.com/myapp/backend:${VERSION}
```

---

## Step 4: 更新 K8s 配置

完整 K8s YAML 模板（ServiceAccount, Deployment, Service, Ingress, Kustomize）见：[references/k8s-manifests.md](references/k8s-manifests.md)

```bash
export PROJECT=myapp
export ENV=main   # main / staging / dev
export VERSION=$(git rev-parse --short HEAD)   # 或 git describe --tags --always（tag 部署）
export IMAGE_REGISTRY=123456.dkr.ecr.us-east-1.amazonaws.com/myapp

# 使用 ns() 函数自动推导 namespace（在 Step 1.5 中定义）
BACKEND_NS=$(ns backend)   # main→myapp-backend  staging→myapp-staging-backend
FRONTEND_NS=$(ns frontend)

envsubst < backend/k8s/deployment.yaml  | kubectl apply -f - -n ${BACKEND_NS}
envsubst < backend/k8s/service.yaml     | kubectl apply -f - -n ${BACKEND_NS}
envsubst < frontend/k8s/deployment.yaml | kubectl apply -f - -n ${FRONTEND_NS}
envsubst < frontend/k8s/service.yaml    | kubectl apply -f - -n ${FRONTEND_NS}
envsubst < k8s/ingress.yaml             | kubectl apply -f -

# 或使用 Kustomize（多环境推荐）
kubectl apply -k infrastructure/k8s/overlays/${ENV}
```

**Secrets 管理**：
```bash
kubectl create secret generic backend-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=jwt-secret='...' \
  -n $(ns backend)
```

---

## Step 5: 数据库迁移（自动检测，按需执行）

迁移文件是幂等的（IF NOT EXISTS / DROP CONSTRAINT IF EXISTS），但每次都跑会产生无意义的 Job 记录。先检测是否有未执行的 migration，有则执行，无则跳过。

**检测逻辑：**

```bash
# 1. 扫描项目中的 migration 文件（按时间戳排序）
MIGRATION_DIR=""
if [ -d "supabase/migrations" ]; then
  MIGRATION_DIR="supabase/migrations"
elif [ -d "migrations" ]; then
  MIGRATION_DIR="migrations"
elif [ -d "db/migrations" ]; then
  MIGRATION_DIR="db/migrations"
fi

if [ -z "$MIGRATION_DIR" ]; then
  echo "⏭️  未发现 migration 目录，跳过数据库迁移"
  MIGRATION_STATUS="SKIPPED（无 migration 目录）"
else
  # 获取所有 .sql migration 文件名（不含路径）
  LOCAL_MIGRATIONS=$(ls ${MIGRATION_DIR}/*.sql 2>/dev/null | xargs -I{} basename {} | sort)

  if [ -z "$LOCAL_MIGRATIONS" ]; then
    echo "⏭️  migration 目录为空，跳过"
    MIGRATION_STATUS="SKIPPED（无 .sql 文件）"
  else
    # 2. 查询数据库中已执行的 migration 记录
    # Supabase 项目用 supabase_migrations.schema_migrations
    # 自托管 PostgreSQL 用 public.schema_migrations（需提前建表）
    DB_URL="${DATABASE_URL:-$(cat .env.local 2>/dev/null | grep DATABASE_URL | cut -d= -f2-)}"

    APPLIED=$(psql "${DB_URL}" -t -c \
      "SELECT version FROM supabase_migrations.schema_migrations ORDER BY version;" \
      2>/dev/null | tr -d ' ' | grep -v '^$' || echo "")

    # 3. 计算差集：本地有但数据库未记录的
    PENDING=""
    for f in $LOCAL_MIGRATIONS; do
      version="${f%.sql}"
      if ! echo "$APPLIED" | grep -qx "$version"; then
        PENDING="$PENDING $f"
      fi
    done

    if [ -z "$PENDING" ]; then
      echo "✅ 所有 migration 已执行，跳过（共 $(echo $LOCAL_MIGRATIONS | wc -w) 个）"
      MIGRATION_STATUS="SKIPPED（无待执行 migration）"
    else
      echo "🔄 发现未执行的 migration：$PENDING"
      echo "📦 执行数量：$(echo $PENDING | wc -w)"

      # 4. 有待执行的 migration → 运行 K8s Job
      envsubst < k8s/migration-job.yaml | kubectl apply -f -
      kubectl wait --for=condition=complete --timeout=300s \
        job/db-migrate-${VERSION} -n ${PROJECT}-${ENV}-backend
      kubectl logs job/db-migrate-${VERSION} -n ${PROJECT}-${ENV}-backend
      MIGRATION_STATUS="EXECUTED（$(echo $PENDING | wc -w) 个 migration）"
    fi
  fi
fi
```

> **注意：** 若项目使用 Prisma，改为检测 `_prisma_migrations` 表；若使用 Alembic，改为检测 `alembic_version` 表。逻辑一致，只需调整查询语句。

---

## Step 6: 监控滚动更新

```bash
kubectl rollout status deployment/backend  -n ${PROJECT}-${ENV}-backend
kubectl rollout status deployment/frontend -n ${PROJECT}-${ENV}-frontend
kubectl get pods --all-namespaces -l app=${PROJECT},env=${ENV}
```

---

## Step 7: 验证部署

```bash
# Port Forward 测试
kubectl port-forward -n ${PROJECT}-${ENV}-backend svc/backend 8080:80
curl http://localhost:8080/health
curl http://localhost:8080/ready

# 端到端
curl https://${DOMAIN}/api/health
curl https://${DOMAIN}/

# 资源使用
kubectl top pods -n ${PROJECT}-${ENV}-backend
```

---

## Step 8: 回滚（如果失败）

```bash
kubectl rollout history deployment/backend -n ${PROJECT}-${ENV}-backend
kubectl rollout undo deployment/backend  -n ${PROJECT}-${ENV}-backend
kubectl rollout undo deployment/frontend -n ${PROJECT}-${ENV}-frontend
# 回滚到指定版本
kubectl rollout undo deployment/backend -n ${PROJECT}-${ENV}-backend --to-revision=3
```

---

## Step 9: 生成部署报告

输出到 `reports/deployment-${ENV}-${VERSION}.md`：

```markdown
## 部署概览
- 环境: ${ENV} | 版本: ${VERSION} | 时间: $(date)

## 部署状态
| 服务 | 状态 | 副本数 |
|------|------|--------|
| backend  | ✅ Running | 3/3 |
| frontend | ✅ Running | 2/2 |

## 数据库迁移
- 状态: ${MIGRATION_STATUS}

## 访问地址
- API: https://${DOMAIN}/api
- 前端: https://${DOMAIN}

## 回滚计划
- 上一版本: ${PREV_VERSION}
- 回滚命令: `kubectl rollout undo deployment/backend -n ${PROJECT}-${ENV}-backend`
```

---

## 注意事项

1. **生产环境**：先在 staging 验证，再部署 prod
2. **数据库迁移**：迁移脚本必须可回滚
3. **Namespace 创建**：必须同步 ResourceQuota + LimitRange
4. **镜像扫描**：`trivy image ${IMAGE_REGISTRY}/backend:${VERSION}`
