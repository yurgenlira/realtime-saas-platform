#!/bin/bash
set -euo pipefail

# System Update
dnf update -y

# Docker Installation
dnf install -y docker git
systemctl enable docker
systemctl start docker

# Clone Repository
git clone https://${github_token}@github.com/yurgenlira/realtime-saas-platform.git /opt/app
cd /opt/app

# Environment Configuration
cat > /opt/app/.env << 'ENVEOF'
DATABASE_URL=postgresql://${db_username}:${db_password}@${db_host}:${db_port}/${db_name}
REDIS_URL=${redis_url}
ENVEOF
chmod 600 /opt/app/.env
chown ec2-user:ec2-user /opt/app/.env

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
