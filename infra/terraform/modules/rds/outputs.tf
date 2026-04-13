output "db_endpoint" {
  description = "RDS instance endpoint (host:port) for application connection"
  value       = aws_db_instance.main.endpoint
}

output "db_host" {
  description = "RDS hostname without port"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "RDS port"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "app_security_group_id" {
  description = "ID of the app Security Group — attach this to EC2 instances"
  value       = aws_security_group.app.id
}

output "rds_security_group_id" {
  description = "ID of the RDS Security Group"
  value       = aws_security_group.rds.id
}
