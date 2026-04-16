variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository in format owner/repo (e.g. org/realtime-saas-platform)"
  type        = string
}

variable "ecr_repository_arn" {
  description = "ARN of the ECR repository to grant push access"
  type        = string
}

variable "ec2_instance_id" {
  description = "EC2 instance ID to grant SSM RunCommand access"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}
