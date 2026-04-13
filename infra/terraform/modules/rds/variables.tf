variable "project_name" {
  description = "Project name, used as a prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment: dev, staging, prod"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where RDS and Security Groups will be created"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the DB Subnet Group"
  type        = list(string)
}

variable "db_name" {
  description = "Name of the initial database to create"
  type        = string
  default     = "webhooks"
}

variable "db_username" {
  description = "Master username for the RDS instance"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master password for the RDS instance"
  type        = string
  sensitive   = true # Prevents the value from appearing in logs and plan output
}

variable "db_instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage size in GB"
  type        = number
  default     = 20
}

variable "backup_retention_days" {
  description = "Number of days to retain automated backups (0 disables backups)"
  type        = number
  default     = 1 # Free tier only allows 1 day
}
