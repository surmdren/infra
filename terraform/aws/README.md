# AWS Terraform Infrastructure

## 目录结构

```
terraform/aws/
├── modules/
│   ├── vpc/              # VPC + 子网 + 路由
│   ├── ec2/              # EC2 实例 + EIP + Key Pair
│   └── security-groups/  # 安全组（SSH/HTTP/HTTPS）
└── environments/
    ├── dev/              # 开发环境
    ├── staging/          # 预生产
    └── prod/             # 生产环境
```

## 快速开始

### 1. 配置 AWS 凭证

```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
# 或者使用 aws configure
```

### 2. 部署 dev 环境

```bash
cd environments/dev

# 填入你的 SSH 公钥
echo 'public_key = "ssh-rsa AAAA..."' >> terraform.tfvars

terraform init
terraform plan
terraform apply
```

### 3. 获取服务器 IP

```bash
terraform output server_public_ip
```

### 4. SSH 连接

```bash
ssh ubuntu@$(terraform output -raw server_public_ip)
```

## 默认配置

| 参数 | dev 默认值 |
|------|-----------|
| Region | ap-northeast-1 (Tokyo) |
| Instance | t3.micro |
| OS | Ubuntu 22.04 |
| Disk | 20 GB gp3 |
| 开放端口 | 22, 80, 443 |

## 销毁环境

```bash
terraform destroy
```
