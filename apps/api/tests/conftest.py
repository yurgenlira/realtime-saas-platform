import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault(
    "SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/000000000000/test-queue"
)
os.environ.setdefault("AWS_REGION", "us-east-1")
