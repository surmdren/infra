variable "project_name"       { type = string }
variable "environment"        { type = string }
variable "vpc_id"             { type = string }
variable "ssh_allowed_cidrs"  {
  type    = list(string)
  default = ["0.0.0.0/0"] # 生产环境请改为你的 IP
}
