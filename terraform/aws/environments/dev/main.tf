locals {
  project_name = "dreamai"
  environment  = "dev"
}

module "vpc" {
  source       = "../../modules/vpc"
  project_name = local.project_name
  environment  = local.environment
}

module "security_groups" {
  source       = "../../modules/security-groups"
  project_name = local.project_name
  environment  = local.environment
  vpc_id       = module.vpc.vpc_id
}

module "ec2" {
  source            = "../../modules/ec2"
  project_name      = local.project_name
  environment       = local.environment
  subnet_id         = module.vpc.public_subnet_ids[0]
  security_group_id = module.security_groups.web_sg_id
  instance_type     = var.instance_type
  public_keys       = var.public_keys
  user_data         = file("${path.module}/../../modules/ec2/user_data.sh")
}
