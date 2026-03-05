# AWS 生产环境基础设施

## 架构图

```
Route 53 (DNS) → CloudFront (CDN) → ALB → EKS Cluster
                                              ├── Frontend Pod (HPA)
                                              ├── Backend Pod (HPA)
                                              └── Worker Pod
                                         ↓
                               RDS | ElastiCache | S3
                                         ↑
                                    CloudWatch
```

## 服务配置

| 服务 | 用途 | 规格建议 | 关键配置 |
|------|------|----------|----------|
| **Route 53** | DNS | 托管区域 | A记录 → ALB，CNAME → CloudFront |
| **CloudFront** | CDN | 按流量计费 | Origin: ALB, 缓存策略, GZIP |
| **ACM** | SSL 证书 | 免费 | 自动续期，泛域名 |
| **ALB** | 负载均衡 | 应用层 | 跨AZ，健康检查，SSL终止 |
| **EKS** | K8s 集群 | 托管控制面 | 多AZ节点组，IRSA角色 |
| **EC2** | 工作节点 | t3.medium (2C4G) | 按需实例，EBS GP3 |
| **RDS** | PostgreSQL | db.t3.medium | 多AZ，自动备份，加密 |
| **ElastiCache** | Redis | cache.t3.micro | 集群模式，故障转移 |
| **S3** | 对象存储 | 标准存储 | 版本控制，生命周期 |
| **ECR** | 容器镜像 | 按存储计费 | 镜像扫描，生命周期 |
| **Secrets Manager** | 密钥管理 | 按密钥数计费 | 自动轮换 |
| **CloudWatch** | 监控日志 | 按日志量计费 | 自定义指标，告警 |

## VPC 网络规划

```yaml
VPC: 10.0.0.0/16
├── Public Subnet 1:  10.0.1.0/24  (AZ-a) - ALB, NAT Gateway
├── Public Subnet 2:  10.0.2.0/24  (AZ-b) - ALB, NAT Gateway
├── Private Subnet 1: 10.0.11.0/24 (AZ-a) - EKS Nodes, RDS
├── Private Subnet 2: 10.0.12.0/24 (AZ-b) - EKS Nodes, RDS
├── Private Subnet 3: 10.0.21.0/24 (AZ-a) - ElastiCache
└── Private Subnet 4: 10.0.22.0/24 (AZ-b) - ElastiCache

安全组:
├── ALB-SG:     80, 443 from 0.0.0.0/0
├── EKS-SG:     30000-32767 from ALB-SG
├── RDS-SG:     5432 from EKS-SG
└── Redis-SG:   6379 from EKS-SG
```

## CI/CD（GitHub Actions → EKS）

```yaml
# .github/workflows/deploy.yml
name: Deploy to EKS
on:
  push:
    branches: [main]
jobs:
  deploy:
    steps:
      - name: Build & Push to ECR
        run: |
          docker build -t $ECR_URI:$GITHUB_SHA .
          docker push $ECR_URI:$GITHUB_SHA
      - name: Deploy to EKS
        run: |
          kubectl set image deployment/backend \
            backend=$ECR_URI:$GITHUB_SHA -n backend
          kubectl rollout status deployment/backend -n backend
```

## HPA 自动扩缩

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: backend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```
