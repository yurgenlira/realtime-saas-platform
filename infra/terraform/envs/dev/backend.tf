terraform {
  backend "s3" {
    bucket         = "realtime-saas-terraform-state-dev"
    key            = "dev/networking/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "realtime-saas-terraform-locks"
    encrypt        = true # Encrypts state at rest using AES-256
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.37"
    }
  }

  required_version = ">= 1.14.0"
}

provider "aws" {
  region = var.aws_region

  # Apply these tags to every resource created by this provider
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
