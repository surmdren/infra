# Supabase on K8s 部署指南

**域名:** `supabase.dreamwiseai.com`  
**访问方式:** Cloudflare Tunnel  
**存储:** 本地 hostPath  
**数据库:** PostgreSQL（K8s 内部）

---

## 文件说明

- `values.yaml` — Helm 配置（包含所有服务配置）
- `local-storage.yaml` — StorageClass 和 PersistentVolume
- `ingress.yaml` — Nginx Ingress + Cloudflare Tunnel 部署
- `secrets.env` — 密钥文件（**不提交 git**，本地保存）

---

## 部署步骤

### 1. 前置条件

```bash
# 确认工具已安装
kubectl version
helm version

# 确认本地 K8s 集群正常
kubectl get nodes
```

### 2. 获取 Cloudflare Tunnel Token

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 进入 **Zero Trust → Access → Tunnels**
3. 创建 Tunnel，名称：`dreamai-local`
4. 复制 Token
5. 配置 Public Hostname：
   - Domain: `supabase.dreamwiseai.com`
   - Service: `http://ingress-nginx-controller.ingress-nginx:80`

### 3. 填入 Cloudflare Token

```bash
kubectl create namespace supabase

kubectl create secret generic cloudflared-secret \
  --from-literal=token=YOUR_TUNNEL_TOKEN \
  --namespace=supabase \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 4. 一键部署

```bash
chmod +x scripts/deploy-supabase.sh
./scripts/deploy-supabase.sh
```

### 5. 验证部署

```bash
# 查看所有 Pod 状态（等待全部 Running）
kubectl get pods -n supabase -w

# 查看服务
kubectl get svc -n supabase

# 查看日志
kubectl logs -n supabase -l app=supabase-studio
```

---

## 访问地址

| 服务 | 地址 |
|------|------|
| Studio 管理界面 | `https://supabase.dreamwiseai.com` |
| API Gateway | `https://supabase.dreamwiseai.com/rest/v1/` |
| Auth | `https://supabase.dreamwiseai.com/auth/v1/` |
| Storage | `https://supabase.dreamwiseai.com/storage/v1/` |
| Realtime | `wss://supabase.dreamwiseai.com/realtime/v1/` |

**管理员账号：**
- 用户名：`supabase`
- 密码：见 `secrets.env` 中 `DASHBOARD_PASSWORD`

---

## 新项目接入

```bash
# 在 Supabase 中为新项目创建独立 schema
./scripts/new-project.sh <project-name>
```

---

## 常见问题

**Pod 一直 Pending？**
```bash
# 检查存储目录是否存在
ls -la /data/supabase/
# 检查 PV 状态
kubectl get pv
```

**Studio 无法访问？**
```bash
# 检查 Cloudflare Tunnel 状态
kubectl logs -n supabase -l app=cloudflared
```

**数据库连接失败？**
```bash
kubectl logs -n supabase -l app=supabase-db
```
