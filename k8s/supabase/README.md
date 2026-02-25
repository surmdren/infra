# Supabase on Kubernetes 部署指南

**域名:** `supabase.dreamwiseai.com` / `supabase-studio.dreamwiseai.com`  
**访问方式:** 宿主机 systemd cloudflared → Cloudflare Tunnel  
**存储:** 本地 hostPath（`~/data/supabase/`）  
**集群类型:** kind（Docker 内）  
**Helm Chart:** `supabase-community/supabase-kubernetes`

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `values.yaml` | Helm 配置（密钥、资源限制、环境变量） |
| `local-storage.yaml` | StorageClass + 3 个 PersistentVolume |
| `ingress.yaml` | NodePort 配置说明（留档） |
| `secrets.env` | 密钥文件（**不提交 git**，本地保存） |

---

## 架构说明

```
外网请求
  └→ Cloudflare CDN (supabase.dreamwiseai.com)
       └→ Cloudflare Tunnel (dreamai tunnel)
            └→ 宿主机 cloudflared (systemd)
                 └→ kind 容器 IP 172.18.0.2
                      ├→ :30086 (NodePort) → supabase-supabase-kong:8000 (API)
                      └→ :30087 (NodePort) → supabase-supabase-studio:3000 (Studio)
```

**关键端口映射（kind extraPortMappings）：**

| 容器 NodePort | 宿主机端口 | 服务 |
|--------------|-----------|------|
| 30086 | 10003 | Kong API Gateway |
| 30087 | 10004 | Studio 管理界面 |

---

## 前置条件

```bash
kubectl version    # 已验证: v1.35.0
helm version       # Helm v3.x
kind               # kind 集群 dreamai-control-plane
```

**宿主机 systemd cloudflared 已配置并运行（`/etc/cloudflared/config.yml`）**

---

## 部署步骤

### 1. 创建存储目录

```bash
# 不需要 sudo！用 home 目录
mkdir -p ~/data/supabase/db ~/data/supabase/storage ~/data/supabase/minio
```

### 2. 创建 K8s 命名空间

```bash
kubectl create namespace supabase
```

### 3. 应用本地存储配置

```bash
kubectl apply -f k8s/supabase/local-storage.yaml
kubectl get pv  # 验证 3 个 PV 已创建
```

### 4. 添加 Helm 仓库

```bash
HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890 \
  helm repo add supabase https://supabase-community.github.io/supabase-kubernetes
HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890 \
  helm repo update
```

> ⚠️ Helm 需要代理才能访问 GitHub Release assets

### 5. 部署 Supabase

```bash
cd /home/ysurmd/github/dreamai/infra
HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890 \
helm install supabase supabase/supabase \
  --namespace supabase \
  --values k8s/supabase/values.yaml \
  --timeout 10m
```

### 6. 配置 containerd 代理（kind 集群拉镜像用）

```bash
docker exec dreamai-control-plane bash -c "
mkdir -p /etc/systemd/system/containerd.service.d/
cat > /etc/systemd/system/containerd.service.d/http-proxy.conf << 'EOF'
[Service]
Environment=\"HTTP_PROXY=http://172.18.0.1:7890\"
Environment=\"HTTPS_PROXY=http://172.18.0.1:7890\"
Environment=\"NO_PROXY=localhost,127.0.0.1,10.96.0.0/12,192.168.0.0/16,172.16.0.0/12\"
EOF
systemctl daemon-reload
systemctl restart containerd
"
```

> ⚠️ 关键：kind 容器内的代理地址是 `172.18.0.1`（Docker 网关），不是 `127.0.0.1`

### 7. 修复 Secret 缺失字段

Helm chart 的 Secret 有几个字段需要手动填充（values.yaml 里设置占位值）：

```bash
# openAiApiKey (studio 需要)
kubectl patch secret -n supabase supabase-dashboard \
  --type='json' \
  -p='[{"op":"add","path":"/data/openAiApiKey","value":"'$(echo -n "placeholder" | base64)'"}]'

# SMTP 在 values.yaml 中已设置占位值
```

### 8. 把 Helm Service 改为 NodePort

Helm 创建的 Service 默认是 ClusterIP，patch 改为 NodePort：

```bash
# Kong API: NodePort 30086 (kind 映射到宿主机 10003)
kubectl patch svc -n supabase supabase-supabase-kong \
  -p '{"spec":{"type":"NodePort","ports":[{"port":8000,"targetPort":8000,"nodePort":30086,"protocol":"TCP","name":"http"}]}}'

# Studio: NodePort 30087 (kind 映射到宿主机 10004)
kubectl patch svc -n supabase supabase-supabase-studio \
  -p '{"spec":{"type":"NodePort","ports":[{"port":3000,"targetPort":3000,"nodePort":30087,"protocol":"TCP","name":"http"}]}}'
```

### 9. 更新 Cloudflare Tunnel 路由（需要 sudo）

```bash
sudo sed -i \
  's|service: http://localhost:30800|service: http://172.18.0.2:30086|; s|service: http://localhost:30300|service: http://172.18.0.2:30087|' \
  /etc/cloudflared/config.yml
sudo systemctl restart cloudflared
```

### 10. 验证

```bash
# Pod 全部 Running
kubectl get pods -n supabase

# 宿主机本地访问测试
curl -o /dev/null -w "%{http_code}" http://127.0.0.1:10003/rest/v1/  # 应返回 401
curl -o /dev/null -w "%{http_code}" http://127.0.0.1:10004           # 应返回 307

# 或者通过 kind 容器 IP
curl -o /dev/null -w "%{http_code}" http://172.18.0.2:30086/rest/v1/ # 401 ✅
curl -o /dev/null -w "%{http_code}" http://172.18.0.2:30087          # 307 ✅
```

---

## 升级配置

修改 `values.yaml` 后：

```bash
HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890 \
helm upgrade supabase supabase/supabase \
  --namespace supabase \
  --values k8s/supabase/values.yaml \
  --timeout 10m
```

---

## 访问地址

| 服务 | 地址 |
|------|------|
| Studio 管理界面 | `https://supabase-studio.dreamwiseai.com` |
| API Gateway | `https://supabase.dreamwiseai.com/rest/v1/` |
| Auth | `https://supabase.dreamwiseai.com/auth/v1/` |
| Storage | `https://supabase.dreamwiseai.com/storage/v1/` |
| Realtime | `wss://supabase.dreamwiseai.com/realtime/v1/` |

**管理员账号：**
- 用户名：`supabase`
- 密码：`cmXyBGFZpC3v5vd`

---

## 已知问题 & 解决方案

### ErrImagePull / TLS handshake timeout
**原因：** kind 容器默认用 `127.0.0.1:7890` 代理，但容器内 127.0.0.1 是自身，不是宿主机。  
**解决：** 为 containerd 配置 `172.18.0.1:7890`（Docker 网关地址）。见步骤 6。

### Kong OOMKilled
**原因：** 默认内存限制太小（128Mi）。  
**解决：** 在 `values.yaml` 中去掉 Kong 的 `limits`（只保留 requests），让 Kong 自由分配。

### CreateContainerConfigError: couldn't find key openAiApiKey
**原因：** Helm chart 的 `supabase-dashboard` Secret 缺少 `openAiApiKey` 字段。  
**解决：** `kubectl patch secret` 手动注入（见步骤 7）。

### NodePort 被占用（30080/30081 等）
**原因：** 其他服务（voice-to-claw）已占用这些端口。  
**解决：** 用 30086/30087，对应 kind 的 Docker 端口映射 10003/10004。

### Helm upgrade 报 EOF
**原因：** Helm 下载 chart tgz 需要访问 GitHub，须走代理。  
**解决：** 在 helm 命令前加 `HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890`。

### K8s cloudflared pod 报 "Tunnel token is not valid"
**原因：** K8s 内的 cloudflared 不需要——宿主机 systemd 已运行 cloudflared。  
**解决：** `kubectl delete deployment -n supabase cloudflared`

---

## Pod 状态参考（部署完成后）

```
supabase-supabase-analytics   Running
supabase-supabase-auth        Running
supabase-supabase-db          Running
supabase-supabase-functions   Running
supabase-supabase-imgproxy    Running
supabase-supabase-kong        Running
supabase-supabase-meta        Running
supabase-supabase-realtime    Running
supabase-supabase-rest        Running
supabase-supabase-storage     Running
supabase-supabase-studio      Running
supabase-supabase-vector      Running
```

---

## 新项目接入 Supabase

在 Studio 中创建新项目，或通过 SQL 创建独立 schema：

```sql
CREATE SCHEMA project_name;
GRANT ALL ON SCHEMA project_name TO supabase_admin;
```
