resource "aws_secretsmanager_secret" "rds" {
  name        = "${var.project_name}/${var.environment}/rds"
  description = "RDS PostgreSQL credentials for ${var.project_name} ${var.environment}"

  recovery_window_in_days = var.recovery_window_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "rds" {
  secret_id = aws_secretsmanager_secret.rds.id

  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
    host     = var.db_host
    port     = tostring(var.db_port)
    dbname   = var.db_name
  })
}
