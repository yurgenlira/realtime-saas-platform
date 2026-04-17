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

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "webhooks"
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
  default     = "redis://localhost:6379"
}

variable "github_token" {
  description = "GitHub Personal Access Token for repository access"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repository in format owner/repo"
  type        = string
  default     = "yurgenlira/realtime-saas-platform"
}

variable "terraform_state_bucket" {
  description = "S3 bucket name storing Terraform state"
  type        = string
  default     = "realtime-saas-terraform-state-dev"
}

variable "terraform_lock_table" {
  description = "DynamoDB table name used for Terraform state locking"
  type        = string
  default     = "realtime-saas-terraform-locks"
}
