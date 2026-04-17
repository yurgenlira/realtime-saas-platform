output "ingestion_queue_url" {
  description = "SQS ingestion queue URL"
  value       = aws_sqs_queue.ingestion.url
}

output "ingestion_queue_arn" {
  description = "SQS ingestion queue ARN"
  value       = aws_sqs_queue.ingestion.arn
}

output "dead_letter_queue_url" {
  description = "Dead letter queue URL"
  value       = aws_sqs_queue.dead_letter.url
}

output "dead_letter_queue_arn" {
  description = "Dead letter queue ARN"
  value       = aws_sqs_queue.dead_letter.arn
}
