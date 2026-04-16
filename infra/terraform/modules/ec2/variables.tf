variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment: dev, staging, prod"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs where EC2 will be placed"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "ID of the app Security Group created in the RDS module"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID for Amazon Linux 2023 in us-east-1"
  type        = string
  # Amazon Linux 2023 AMI — update periodically via: aws ssm get-parameter
  # --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64
  default = "ami-0ea87431b78a82070"
}

variable "db_host" {
  description = "RDS instance hostname"
  type        = string
}

variable "db_port" {
  description = "RDS instance port"
  type        = number
  default     = 5432
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database master username"
  type        = string
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
  default     = "redis://localhost:6379"
}

variable "github_token" {
  description = "GitHub Personal Access Token for cloning the repository"
  type        = string
  sensitive   = true
}

variable "ecr_repository_arn" {
  description = "ARN of the ECR repository to grant pull access to the EC2 Instance Profile"
  type        = string
}
