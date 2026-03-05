output "instance_id"        { value = aws_instance.main.id }
output "private_ip"         { value = aws_instance.main.private_ip }
output "public_ip"          { value = var.create_eip ? aws_eip.main[0].public_ip : aws_instance.main.public_ip }
