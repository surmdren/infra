---
name: infrastructure-provisioner
description: 根据 TechSolution 方案准备基础设施环境。支持本地测试环境（Local K8s + Helm Charts）和生产环境（AWS/阿里云 + Terraform）。支持 Supabase 模式：检测到使用 Supabase 时，自动从 ~/.dreamai-env 读取共享凭据，按项目目录名自动创建独立 Schema（隔离多项目数据），跳过 PostgreSQL Helm 安装。Redis 仍需独立部署（K8s 用 Helm，Vercel 项目推荐 Upstash）。本地环境使用 Helm Chart，云服务仅配置访问密钥。生产环境使用 Terraform 创建完整云资源。所有基础设施文件放在项目根目录 infrastructure/，环境变量文件自动加入 .gitignore。适用于项目启动、环境初始化、开发环境搭建。当用户提到"基础设施"、"准备环境"、"部署环境"、"创建数据库"、"安装 Redis"、"配置 Supabase"时触发。
---

# 基础设施准备

## Overview

```
infrastructure/
├── .env.local / .env.production   # 环境变量（git 不跟踪）
├── .gitignore
├── terraform/aws/ or alicloud/    # Terraform 配置
├── helm/                          # Helm values
└── scripts/init.sh                # 首次初始化（一次性）
```

两种环境模式：
- **测试环境**：本地 kind 集群 + Helm Charts
- **生产环境**：AWS 或阿里云 + Terraform

---

## Step 1: 环境确认

```bash
# 1. 创建目录结构
mkdir -p infrastructure/terraform/{aws,alicloud} infrastructure/helm infrastructure/scripts

# 2. 配置 .gitignore
cat > infrastructure/.gitignore << 'EOF'
.env.local
.env.production
.env.*.local
*.tfstate
*.tfstate.*
*.tfvars
!example.tfvars
.terraform/
.terraform.lock.hcl
EOF
```

询问用户：
1. **目标环境**：testing（本地 K8s）还是 production（AWS/阿里云）？
2. **数据库模式**：Supabase 托管 还是 K8s 自托管 PostgreSQL？

> 判断依据：若 TechSolution 中提到 Supabase 或使用 Vercel + Next.js，推荐 Supabase 模式。

---

## Step 2: 本地测试环境（Local K8s）

### 2.1 添加 Helm 仓库 + 创建 Namespace

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami && helm repo update

kubectl create namespace postgres
kubectl create namespace redis
kubectl create namespace app
```

> **强制规则：创建任何 Namespace，必须同步创建 ResourceQuota + LimitRange。**

```bash
for NS in postgres redis app; do
  kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ${NS}-quota
  namespace: ${NS}
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 2Gi
    limits.cpu: "2"
    limits.memory: 4Gi
    pods: "20"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: ${NS}-limits
  namespace: ${NS}
spec:
  limits:
    - type: Container
      default: { cpu: "500m", memory: "512Mi" }
      defaultRequest: { cpu: "100m", memory: "128Mi" }
      max: { cpu: "2", memory: "4Gi" }
EOF
done
```

### 2.2-A PostgreSQL（K8s 自托管，非 Supabase）

```bash
helm install postgres bitnami/postgresql \
  --namespace postgres \
  --set auth.postgresPassword=devpassword \
  --set primary.service.type=NodePort \
  --set primary.service.nodePort=30432
# 连接: localhost:30432 / postgres / devpassword
```

### 2.2-B Supabase 模式（跳过 PostgreSQL Helm）

多项目共享同一自托管 Supabase 实例（`~/.dreamai-env` 已配置），通过独立 Schema 隔离：

```
同一 Supabase 实例（192.168.50.189:10003）
├── schema: project_a  ← 项目 A
├── schema: project_b  ← 项目 B
└── schema: public     ← Supabase 内置
```

操作步骤：

1. **读取共享环境变量**（无需手动填写）：
```bash
source ~/.dreamai-env
# 自动获得: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
```

2. **自动推导 schema 名**：取当前项目目录名，`-` 转 `_`，全小写：
```bash
SCHEMA_NAME=$(basename $(pwd) | tr '-' '_' | tr '[:upper:]' '[:lower:]')
echo "Schema: $SCHEMA_NAME"
```

3. **创建项目专属 Schema**（SQL Editor 执行）：
```sql
CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};
GRANT USAGE ON SCHEMA {SCHEMA_NAME} TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA {SCHEMA_NAME}
  GRANT ALL ON TABLES TO anon, authenticated, service_role;
-- Settings → API → Extra Search Path 添加: {SCHEMA_NAME}
```

> ⚠️ 所有建表迁移必须指定 schema（如 `CREATE TABLE {SCHEMA_NAME}.users`），严禁写入 `public` schema，避免污染其他项目数据。

⚠️ Key 安全边界：
- `ANON_KEY`：可前端使用，**必须配置 RLS**
- `SERVICE_ROLE_KEY`：**只能在后端使用**，严禁提交 Git

### 2.3 部署 Redis

**K8s 项目**：
```bash
helm install redis bitnami/redis \
  --namespace redis \
  --set auth.enabled=false \
  --set master.service.type=NodePort \
  --set master.service.nodePort=30379
# 连接: localhost:30379
```

**Vercel 项目**：使用 [Upstash Redis](https://upstash.com)（Serverless，按请求计费），获取 `UPSTASH_REDIS_REST_URL` 和 `UPSTASH_REDIS_REST_TOKEN`。

---

## Step 3: 生产环境（Terraform）

完整 Terraform 配置（AWS + 阿里云）见：[references/terraform-configs.md](references/terraform-configs.md)

```bash
cd infrastructure/terraform/aws  # 或 alicloud
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -auto-approve -var-file="terraform.tfvars"
terraform output
```

---

## Step 4: 生成环境配置文件

`.env.local` 模板（Supabase 模式 / K8s 模式）和 `.env.production` 模板见：[references/env-and-init.md](references/env-and-init.md)

---

## Step 5: 项目初始化脚本（scripts/init.sh）

> **仅在项目首次搭建时执行一次**，不是每次部署都运行。

完整的 `init.sh` 脚本（含 Supabase Schema 创建、Prisma/Drizzle 迁移、连接验证）见：[references/env-and-init.md](references/env-and-init.md)

```bash
chmod +x infrastructure/scripts/init.sh
# 填写 .env.local 后执行：
bash infrastructure/scripts/init.sh
```

---

## 成功标准

**通用**：
- [ ] `infrastructure/` 目录结构已创建
- [ ] `.gitignore` 已配置，敏感文件不被跟踪
- [ ] 环境变量文件 `.env.local` 已生成并填写

**Supabase 模式**：
- [ ] Supabase Schema 已创建并配置 Extra Search Path
- [ ] 跳过 PostgreSQL Helm 安装
- [ ] Upstash Redis 已配置（Vercel 项目）

**K8s 自托管模式**：
- [ ] 每个 Namespace 已创建 ResourceQuota + LimitRange
- [ ] PostgreSQL + Redis Helm 部署成功，连接验证通过

**生产环境**：
- [ ] Terraform apply 成功
- [ ] 所有云资源已就绪
