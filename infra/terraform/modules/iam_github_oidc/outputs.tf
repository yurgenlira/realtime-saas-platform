output "role_arn" {
  description = "ARN of the IAM Role to be used in GitHub Actions (aws-actions/configure-aws-credentials)"
  value       = aws_iam_role.github_actions.arn
}
