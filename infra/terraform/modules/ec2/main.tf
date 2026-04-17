# ---------------------------------------------------
# IAM Role
# ---------------------------------------------------
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-${var.environment}-ec2-role"

  # Trust policy: only EC2 service can assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-ec2-role"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Attach AWS managed policy for CloudWatch Logs agent
resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Attach AWS managed policy for SSM Session Manager (SSH-less access)
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ---------------------------------------------------
# Instance Profile
# ---------------------------------------------------
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-${var.environment}-ec2-profile"
  role = aws_iam_role.ec2_role.name

  tags = {
    Name        = "${var.project_name}-${var.environment}-ec2-profile"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ---------------------------------------------------
# Add HTTP inbound rule to security group
# ---------------------------------------------------
resource "aws_security_group_rule" "app_http_inbound" {
  type              = "ingress"
  security_group_id = var.app_security_group_id
  description       = "Allow HTTP traffic to FastAPI (port 8000)"
  from_port         = 8000
  to_port           = 8000
  protocol          = "tcp"
  cidr_blocks       = ["10.0.0.0/16"] # VPC CIDR — internal traffic only
}

# ---------------------------------------------------
# EC2 Instance
# ---------------------------------------------------
resource "aws_instance" "app" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.private_subnet_ids[0] # Private subnet
  vpc_security_group_ids = [var.app_security_group_id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  # Bootstrap script: runs once on first boot
  user_data_base64 = base64encode(templatefile("${path.module}/user_data.sh", {
    db_host      = var.db_host
    db_port      = var.db_port
    db_name      = var.db_name
    db_username  = var.db_username
    db_password  = var.db_password
    redis_url    = var.redis_url
    github_token = var.github_token
    project      = var.project_name
    environment  = var.environment
  }))

  # Ensure instance profile is ready before EC2 launches
  depends_on = [aws_iam_instance_profile.ec2_profile]

  tags = {
    Name        = "${var.project_name}-${var.environment}-app-server"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ---------------------------------------------------
# ECR Pull Policy
# ---------------------------------------------------
resource "aws_iam_role_policy" "ecr_pull" {
  name = "${var.project_name}-${var.environment}-ecr-pull"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = var.ecr_repository_arn
      }
    ]
  })
}
