output "db_endpoint" {
  value = module.rds.db_endpoint
}

output "db_host" {
  value = module.rds.db_host
}

output "app_security_group_id" {
  value = module.rds.app_security_group_id
}
