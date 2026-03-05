variable "project_name"       { type = string }
variable "environment"        { type = string }
variable "subnet_id"          { type = string }
variable "security_group_id"  { type = string }

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "root_volume_size" {
  type    = number
  default = 100
}

variable "public_keys" {
  description = "List of SSH public keys"
  type        = list(string)
  default     = []
}

variable "create_eip" {
  description = "Allocate Elastic IP"
  type        = bool
  default     = true
}

variable "user_data" {
  description = "Cloud-init script"
  type        = string
  default     = ""
}
