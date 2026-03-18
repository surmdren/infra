# GitHub Actions Self-hosted Runner (Kind)

使用 Actions Runner Controller (ARC) 在 Kind 上部署 GitHub Actions Self-hosted Runner。

## 安装步骤

### 1. 安装 cert-manager
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=120s
```

### 2. 安装 ARC
```bash
helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller
helm repo update
helm upgrade --install arc actions-runner-controller/actions-runner-controller \
  --namespace arc-system \
  --create-namespace \
  -f values.yaml
```

### 3. 创建 GitHub Token Secret
```bash
# GitHub → Settings → Developer settings → Personal access tokens (classic)
# 权限: repo, workflow, admin:org → read:org
kubectl create secret generic github-token \
  --namespace github-runner \
  --from-literal=github_token=<YOUR_GITHUB_PAT>
```

### 4. 部署 Runner
```bash
kubectl apply -f namespace.yaml
kubectl apply -f runner-deployment.yaml
```

### 5. 验证
```bash
kubectl get runners -n github-runner
kubectl get pods -n github-runner
```

## 注意（Kind 环境）
- Kind 网络使用 172.18.0.0/16，runner 可正常访问外网
- Docker-in-Docker 在 kind 里需要特权模式，已在 runner-deployment.yaml 中配置
- 资源按本机实际情况调整
