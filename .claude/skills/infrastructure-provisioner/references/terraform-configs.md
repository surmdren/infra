# Terraform 生产环境配置

## AWS - main.tf

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" { region = var.aws_region }

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier        = "myapp-postgres"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  max_allocated_storage = 100
  db_name  = "myapp"
  username = "admin"
  password = var.db_password
  skip_final_snapshot = false
  final_snapshot_identifier = "myapp-postgres-final"
  vpc_security_group_ids = [aws_security_group.db.id]
  tags = { Name = "myapp-postgres", Env = "production" }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "myapp-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  engine_version       = "7.0"
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
  tags = { Name = "myapp-redis", Env = "production" }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "myapp-redis-subnet"
  subnet_ids = var.subnet_ids
}

# S3 Bucket
resource "aws_s3_bucket" "main" {
  bucket = "myapp-storage-${random_id.bucket_suffix.hex}"
  tags = { Name = "myapp-storage", Env = "production" }
}

resource "random_id" "bucket_suffix" { byte_length = 4 }

# EKS Cluster（可选）
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "~> 19.0"
  cluster_name    = "myapp-cluster"
  cluster_version = "1.27"
  vpc_id          = var.vpc_id
  subnet_ids      = var.subnet_ids
  eks_managed_node_groups = {
    general = {
      desired_size   = 2
      min_size       = 2
      max_size       = 4
      instance_types = ["t3.small"]
      capacity_type  = "ON_DEMAND"
    }
  }
}
```

---

## 阿里云 - main.tf

```hcl
terraform {
  required_providers {
    alicloud = { source = "aliyun/alicloud", version = "~> 1.200" }
  }
}

provider "alicloud" { region = var.region }

# RDS PostgreSQL
resource "alicloud_db_instance" "main" {
  engine           = "PostgreSQL"
  engine_version   = "13.0"
  instance_type    = "pg.n2.small.1"
  instance_storage = 20
  db_instance_name = "myapp-postgres"
  account_name     = "admin"
  account_password = var.db_password
  security_ips     = var.security_ip_list
  tags = { Name = "myapp-postgres", Env = "production" }
}

# Redis
resource "alicloud_kvstore_instance" "main" {
  instance_name  = "myapp-redis"
  instance_class = "redis.master.small.default"
  engine_version = "7.0"
  security_ips   = var.security_ip_list
  tags = { Name = "myapp-redis", Env = "production" }
}

# OSS Bucket
resource "alicloud_oss_bucket" "main" {
  bucket = "myapp-storage-${random_id.bucket_suffix.hex}"
  acl    = "private"
  tags   = { Name = "myapp-storage", Env = "production" }
}

resource "random_id" "bucket_suffix" { byte_length = 4 }
```

---

## 执行步骤

```bash
cd infrastructure/terraform/aws   # 或 alicloud

terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -auto-approve -var-file="terraform.tfvars"
terraform output
```
