output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

output "private_ip" {
  description = "Private IP address of the EC2 instance within the VPC"
  value       = aws_instance.app.private_ip
}

output "iam_role_arn" {
  description = "ARN of the IAM Role"
  value       = aws_iam_role.ec2_role.arn
}

output "instance_profile_name" {
  description = "Name of the IAM Instance Profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}
