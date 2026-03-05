variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1" # Tokyo
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "dreamai"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}
