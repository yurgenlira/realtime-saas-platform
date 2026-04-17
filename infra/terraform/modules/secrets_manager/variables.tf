variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment: dev, staging, prod"
  type        = string
}

variable "db_username" {
  description = "RDS master username"
  type        = string
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "db_host" {
  description = "RDS endpoint hostname"
  type        = string
}

variable "db_port" {
  description = "RDS port"
  type        = number
  default     = 5432
}

variable "db_name" {
  description = "RDS database name"
  type        = string
}

variable "recovery_window_days" {
  description = "Days before secret deletion becomes permanent (0 = immediate, use 7+ in prod)"
  type        = number
  default     = 0
}
