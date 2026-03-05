output "instance_ids"  { value = aws_instance.main[*].id }
output "private_ips"   { value = aws_instance.main[*].private_ip }
output "public_ips"    { value = var.create_eip ? aws_eip.main[*].public_ip : [] }
