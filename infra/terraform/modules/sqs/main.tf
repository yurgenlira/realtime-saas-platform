resource "aws_sqs_queue" "dead_letter" {
  name                      = "${var.project_name}-${var.environment}-dead-letter"
  message_retention_seconds = 1209600 # 14-day retention: investigation window for failed messages

  tags = {
    Name        = "${var.project_name}-${var.environment}-dead-letter"
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "ingestion" {
  name                       = "${var.project_name}-${var.environment}-ingestion"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600 # 4-day retention: sufficient for normal processing cycles

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dead_letter.arn
    maxReceiveCount     = 5
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-ingestion"
    Environment = var.environment
  }
}
