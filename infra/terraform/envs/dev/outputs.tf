output "db_endpoint" {
  value = module.rds.db_endpoint
}

output "db_host" {
  value = module.rds.db_host
}

output "app_security_group_id" {
  value = module.rds.app_security_group_id
}

output "ec2_instance_id" {
  value = module.ec2.instance_id
}

output "ec2_private_ip" {
  value = module.ec2.private_ip
}

output "ecr_api_repository_url" {
  value = module.ecr_api.repository_url
}

output "ecr_worker_repository_url" {
  value = module.ecr_worker.repository_url
}

output "github_actions_role_arn" {
  value = module.iam_github_oidc.role_arn
}

output "sqs_ingestion_queue_url" {
  value = module.sqs.ingestion_queue_url
}

output "sqs_dead_letter_queue_url" {
  value = module.sqs.dead_letter_queue_url
}

output "rds_secret_name" {
  value = module.secrets_manager.secret_name
}
