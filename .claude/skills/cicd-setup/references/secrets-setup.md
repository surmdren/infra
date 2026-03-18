# GitHub Secrets 配置指南

## 需要配置的 Secrets

在 GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret：

| Secret 名称 | 用途 | 如何获取 |
|-------------|------|---------|
| `ACR_USERNAME` | 阿里云 ACR 登录用户名 | 阿里云控制台 → 容器镜像服务 → 访问凭证 |
| `ACR_PASSWORD` | 阿里云 ACR 登录密码 | 同上，点击"设置固定密码" |
| `KUBECONFIG_STAGING` | Staging K8s 集群访问凭证（Base64） | 见下方获取方式 |
| `KUBECONFIG_PROD` | Prod K8s 集群访问凭证（Base64） | 见下方获取方式 |
| `STAGING_URL` | Staging 环境 URL | 如 `https://staging.myapp.com` |
| `PROD_URL` | Prod 环境 URL | 如 `https://myapp.com` |

---

## 如何获取 KUBECONFIG（Base64 格式）

### 本地 k3s 集群

```bash
# 获取 kubeconfig 并 Base64 编码
cat ~/.kube/config | base64 -w 0
# 将输出的内容粘贴到 GitHub Secret
```

### 阿里云 ACK 集群

1. 进入阿里云控制台 → 容器服务 ACK → 集群列表
2. 点击集群 → 连接信息 → 公网访问
3. 复制 KubeConfig 内容
4. 本地运行编码：`echo "粘贴内容" | base64 -w 0`

---

## 如何配置 GitHub Environment（手动审批）

`deploy-prod.yml` 使用了 `environment: production`，需要在 GitHub 配置审批规则：

1. 进入仓库 → **Settings** → **Environments**
2. 点击 **New environment**，命名为 `production`
3. 勾选 **Required reviewers**
4. 添加需要审批的 GitHub 用户（即你自己）
5. 保存

配置后，每次 deploy-prod workflow 运行时，会在审批步骤暂停，在 Actions 界面显示 "Waiting for review"，点击 **Review deployments** → **Approve** 才继续部署。

---

## 阿里云 ACR 完整配置步骤

1. 登录阿里云控制台 → 搜索"容器镜像服务"
2. 选择"个人版"（免费）或"企业版"
3. 创建命名空间（如 `mycompany`）
4. 创建镜像仓库（如 `my-app`），选择私有
5. 进入"访问凭证"，设置固定密码
6. Registry 地址格式：`registry.cn-{region}.aliyuncs.com/{namespace}/{repo}`
   - 例：`registry.cn-hangzhou.aliyuncs.com/mycompany/my-app`

### 常用 Region

| Region | 地址 |
|--------|------|
| 华东 1（杭州） | `registry.cn-hangzhou.aliyuncs.com` |
| 华北 2（北京） | `registry.cn-beijing.aliyuncs.com` |
| 华南 1（深圳） | `registry.cn-shenzhen.aliyuncs.com` |
| 上海 | `registry.cn-shanghai.aliyuncs.com` |
