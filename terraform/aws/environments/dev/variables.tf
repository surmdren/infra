variable "aws_region" {
  type    = string
  default = "ap-northeast-1"
}

variable "instance_type" {
  type    = string
  default = "t3.xlarge"
}

variable "public_keys" {
  type    = list(string)
  default = []
}
