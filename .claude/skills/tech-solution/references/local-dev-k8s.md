# 本地 K8s 开发环境

## K8s 集群选型

| 工具 | 优势 | 推荐度 |
|------|------|---------|
| **Kind** | 轻量级、快速启动，CI/CD 友好 | ⭐⭐⭐⭐⭐ |
| **minikube** | 功能完整、支持插件 | ⭐⭐⭐⭐ |
| **k3s** | 资源占用小、生产级 | ⭐⭐⭐ |

**推荐**: Kind (Kubernetes in Docker)

## Namespace 规划

> **强制规则：创建任何 Namespace，必须同步创建 ResourceQuota 和 LimitRange。**

```yaml
- infrastructure     # PostgreSQL, Redis, MinIO 等中间件
- monitoring        # Prometheus, Grafana（可选）
- frontend          # React/Vue 应用
- backend           # API 服务
- workers           # 后台任务处理
```

## 中间件部署（Helm Charts）

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace infrastructure --create-namespace \
  --set auth.postgresPassword=localdev123 \
  --set auth.database=app_db

# Redis
helm install redis bitnami/redis \
  --namespace infrastructure \
  --set auth.password=localdev123

# MinIO（可选）
helm repo add minio https://charts.min.io/
helm install minio minio/minio \
  --namespace infrastructure \
  --set rootUser=minioadmin \
  --set rootPassword=minioadmin123
```

## 本地访问

```bash
# Port Forward（推荐）
kubectl port-forward svc/postgres-postgresql 5432:5432 -n infrastructure
kubectl port-forward svc/redis-master 6379:6379 -n infrastructure
kubectl port-forward svc/frontend 3000:3000 -n frontend
kubectl port-forward svc/backend 8080:8080 -n backend
```

## 环境变量（.env.local）

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_db
DB_USER=postgres
DB_PASSWORD=localdev123

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=localdev123

S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_BUCKET=app-bucket

NODE_ENV=development
API_BASE_URL=http://localhost:8080
FRONTEND_URL=http://localhost:3000
```

## 常用调试命令

```bash
kubectl get pods -A
kubectl logs -f deployment/backend -n backend
kubectl exec -it deployment/backend -n backend -- /bin/bash
kubectl describe svc backend -n backend
kubectl get ingress -A
```
