output "db_endpoint" {
  value = module.rds.db_endpoint
}

output "db_host" {
  value = module.rds.db_host
}

output "app_security_group_id" {
  value = module.rds.app_security_group_id
}

output "ec2_instance_id" {
  value = module.ec2.instance_id
}

output "ec2_private_ip" {
  value = module.ec2.private_ip
}
