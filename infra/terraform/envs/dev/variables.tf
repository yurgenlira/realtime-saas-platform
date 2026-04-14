variable "project_name" {
  description = "Project name prefix applied to all resources"
  default     = "realtime-saas"
}

variable "environment" {
  description = "Deployment environment identifier"
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region where resources will be provisioned"
  default     = "us-east-1"
}

variable "db_username" {
  description = "Master username for RDS"
  default     = "postgres"
}

variable "db_password" {
  description = "Master password for RDS"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub Personal Access Token for repository access"
  type        = string
  sensitive   = true
}
