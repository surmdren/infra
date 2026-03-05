terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # 可选：使用 S3 存储 tfstate
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "aws/terraform.tfstate"
  #   region = "ap-northeast-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
