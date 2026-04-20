#!/bin/bash
set -euo pipefail

# System Update
dnf update -y

# Docker Installation
dnf install -y docker git jq
systemctl enable docker
systemctl start docker

# Clone Repository
git clone https://${github_token}@github.com/yurgenlira/realtime-saas-platform.git /opt/app
cd /opt/app

# Fetch RDS credentials from Secrets Manager using Instance Profile
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "${rds_secret_name}" \
  --region "${aws_region}" \
  --query SecretString \
  --output text)

DB_USERNAME=$(echo "$SECRET_JSON" | jq -r '.username')
DB_PASSWORD=$(echo "$SECRET_JSON" | jq -r '.password')
DB_HOST=$(echo "$SECRET_JSON"     | jq -r '.host')
DB_PORT=$(echo "$SECRET_JSON"     | jq -r '.port')
DB_NAME=$(echo "$SECRET_JSON"     | jq -r '.dbname')

cat > /opt/app/.env << EOF
DATABASE_URL=postgresql://$${DB_USERNAME}:$${DB_PASSWORD}@$${DB_HOST}:$${DB_PORT}/$${DB_NAME}
SQS_QUEUE_URL=${sqs_queue_url}
EOF
chmod 600 /opt/app/.env
chown ec2-user:ec2-user /opt/app/.env

# Clear shell variables — credentials must not persist in the cloud-init parent process environment
unset SECRET_JSON DB_USERNAME DB_PASSWORD DB_HOST DB_PORT DB_NAME

# Build Docker Image
docker build -f docker/Dockerfile --target runner -t ${project}-api:latest .

# Launch API Container
docker run -d \
  --name api \
  --restart unless-stopped \
  --env-file /opt/app/.env \
  -p 8000:8000 \
  ${project}-api:latest

# Install CloudWatch Agent
dnf install -y amazon-cloudwatch-agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -s -c default
