---
name: dev-deploy
description: 将应用部署到Kubernetes集群。构建容器镜像、推送到镜像仓库、更新K8s配置、执行数据库迁移、验证部署状态、回滚支持。本地测试环境使用 kind 集群（无需推送镜像仓库，用 kind load 加载本地镜像）；生产环境适用于AWS EKS、阿里云ACK。支持多环境部署（dev/staging/prod）。当用户提到"部署"、"发布"、"上线"、"deploy"、"K8s部署"时触发。
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
格式: <project>-<env>-<component>
示例: myapp-dev-backend / myapp-prod-frontend / myapp-prod-infra
```

| 环境 | 用途 | 资源规格 |
|------|------|---------|
| dev | 开发测试 | 低配置 |
| staging | 预发布 | 中等配置 |
| prod | 生产环境 | 高配置 + HPA |

> **强制规则：创建 Namespace 时必须同步创建 ResourceQuota + LimitRange。**

```bash
kubectl create namespace ${PROJECT}-${ENV}-backend
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota
  namespace: ${PROJECT}-${ENV}-backend
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
  namespace: ${PROJECT}-${ENV}-backend
spec:
  limits:
    - type: Container
      default: { cpu: "500m", memory: "512Mi" }
      defaultRequest: { cpu: "100m", memory: "128Mi" }
EOF
```

---

## Step 1: 部署前检查

```bash
cat TechSolution/infrastructure/kubernetes.md
cat DevPlan/checklist.md
# 确认：Dockerfile 存在 / K8s 配置文件存在 / kubectl 已配置 / 镜像仓库权限
```

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

**本地 kind 集群**（无需推送远程仓库，直接加载到 kind）：
```bash
kind load docker-image backend:${VERSION} --name ${KIND_CLUSTER_NAME:-kind}
kind load docker-image frontend:${VERSION} --name ${KIND_CLUSTER_NAME:-kind}
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
export ENV=staging
export VERSION=$(git describe --tags --always)
export IMAGE_REGISTRY=123456.dkr.ecr.us-east-1.amazonaws.com/myapp

envsubst < backend/k8s/deployment.yaml | kubectl apply -f -
envsubst < backend/k8s/service.yaml    | kubectl apply -f -
envsubst < frontend/k8s/deployment.yaml | kubectl apply -f -
envsubst < frontend/k8s/service.yaml    | kubectl apply -f -
envsubst < k8s/ingress.yaml             | kubectl apply -f -

# 或使用 Kustomize（多环境推荐）
kubectl apply -k infrastructure/k8s/overlays/${ENV}
```

**Secrets 管理**：
```bash
kubectl create secret generic backend-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=jwt-secret='...' \
  -n ${PROJECT}-${ENV}-backend
```

---

## Step 5: 执行数据库迁移

```bash
envsubst < k8s/migration-job.yaml | kubectl apply -f -
kubectl wait --for=condition=complete --timeout=300s \
  job/db-migrate-${VERSION} -n ${PROJECT}-${ENV}-backend
kubectl logs job/db-migrate-${VERSION} -n ${PROJECT}-${ENV}-backend
```

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
- 状态: ✅ Success

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
