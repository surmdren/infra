data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd*/ubuntu-*-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

locals {
  ssh_keys_block = length(var.public_keys) > 0 ? join("\n", var.public_keys) : ""
  user_data_final = length(var.public_keys) > 0 ? "${var.user_data}\n\n# SSH keys\nmkdir -p /home/ubuntu/.ssh && chmod 700 /home/ubuntu/.ssh\ncat >> /home/ubuntu/.ssh/authorized_keys << 'EOF'\n${local.ssh_keys_block}\nEOF\nchmod 600 /home/ubuntu/.ssh/authorized_keys && chown -R ubuntu:ubuntu /home/ubuntu/.ssh" : var.user_data
}

resource "aws_instance" "main" {
  count                  = var.instance_count
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_ids[count.index % length(var.subnet_ids)]
  vpc_security_group_ids = [var.security_group_id]
  key_name               = null

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
  }

  user_data = local.user_data_final

  tags = {
    Name = "${var.project_name}-${var.environment}-server-${count.index + 1}"
  }
}

resource "aws_eip" "main" {
  count    = var.create_eip ? var.instance_count : 0
  instance = aws_instance.main[count.index].id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-eip-${count.index + 1}"
  }
}
