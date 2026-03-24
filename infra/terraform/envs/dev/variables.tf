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
