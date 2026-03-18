# GitHub Actions Self-hosted Runner (K3s)

使用 Actions Runner Controller (ARC) 在 K3s 上部署 GitHub Actions Self-hosted Runner。

## 安装步骤

### 1. 安装 cert-manager（ARC 依赖）
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
kubectl wait --namespace cert-manager --for=condition=ready pod --selector=app.kubernetes.io/instance=cert-manager --timeout=120s
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
# 在 GitHub → Settings → Developer settings → Personal access tokens
# 权限需要：repo, workflow, admin:org (如果是 org runner)
kubectl create secret generic github-token \
  --namespace github-runner \
  --from-literal=github_token=<YOUR_GITHUB_TOKEN>
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

## 目录结构
- `values.yaml` - ARC Helm Chart 配置
- `namespace.yaml` - Runner 命名空间
- `runner-deployment.yaml` - RunnerDeployment 资源
- `secret.yaml.example` - Secret 模板（不提交真实 token）
