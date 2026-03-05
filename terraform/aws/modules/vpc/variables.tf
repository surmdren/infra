variable "project_name" { type = string }
variable "environment"  { type = string }

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.0.0/20", "10.0.16.0/20"]
}

variable "availability_zones" {
  type    = list(string)
  default = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.32.0/20", "10.0.48.0/20"]
}
