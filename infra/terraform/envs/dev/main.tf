module "networking" {
  source = "../../modules/networking"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = "10.0.0.0/16"
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.3.0/24", "10.0.4.0/24"]
  availability_zones   = ["us-east-1a", "us-east-1b"]
}

module "rds" {
  source = "../../modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids

  db_name     = "webhooks"
  db_username = var.db_username
  db_password = var.db_password
}

module "ec2" {
  source = "../../modules/ec2"

  project_name          = var.project_name
  environment           = var.environment
  private_subnet_ids    = module.networking.private_subnet_ids
  app_security_group_id = module.rds.app_security_group_id

  github_token       = var.github_token
  ecr_repository_arn = module.ecr.repository_arn
  aws_region         = var.aws_region
  rds_secret_arn     = module.secrets_manager.secret_arn
  rds_secret_name    = module.secrets_manager.secret_name
  sqs_queue_arn      = module.sqs.ingestion_queue_arn
  sqs_queue_url      = module.sqs.ingestion_queue_url
}

module "ecr" {
  source       = "../../modules/ecr"
  project_name = var.project_name
  environment  = var.environment
}

module "iam_github_oidc" {
  source                 = "../../modules/iam_github_oidc"
  project_name           = var.project_name
  github_repo            = var.github_repo
  ecr_repository_arn     = module.ecr.repository_arn
  ec2_instance_id        = module.ec2.instance_id
  aws_region             = var.aws_region
  terraform_state_bucket = var.terraform_state_bucket
  terraform_lock_table   = var.terraform_lock_table
}

module "sqs" {
  source       = "../../modules/sqs"
  project_name = var.project_name
  environment  = var.environment
}

module "secrets_manager" {
  source               = "../../modules/secrets_manager"
  project_name         = var.project_name
  environment          = var.environment
  db_username          = var.db_username
  db_password          = var.db_password
  db_host              = module.rds.db_host
  db_port              = 5432
  db_name              = var.db_name
  recovery_window_days = 0
}
