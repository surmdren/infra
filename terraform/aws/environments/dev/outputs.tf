output "server1_public_ip"  { value = module.ec2_public.public_ips }
output "server1_private_ip" { value = module.ec2_public.private_ips }
output "server2_private_ip" { value = module.ec2_private.private_ips }
output "vpc_id"             { value = module.vpc.vpc_id }
output "private_subnet_ids" { value = module.vpc.private_subnet_ids }
