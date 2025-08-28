# Output values
output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.crypto_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.environment}"
}

output "s3_charts_bucket" {
  description = "S3 bucket for chart storage"
  value       = aws_s3_bucket.charts.bucket
}

output "s3_lambda_artifacts_bucket" {
  description = "S3 bucket for Lambda artifacts"
  value       = aws_s3_bucket.lambda_artifacts.bucket
}

output "dynamodb_pattern_cache_table" {
  description = "DynamoDB pattern cache table name"
  value       = aws_dynamodb_table.pattern_cache.name
}

output "dynamodb_market_data_table" {
  description = "DynamoDB market data table name"
  value       = aws_dynamodb_table.market_data.name
}

output "dynamodb_predictions_table" {
  description = "DynamoDB predictions table name"
  value       = aws_dynamodb_table.predictions.name
}

output "lambda_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_role.arn
}

output "data_ingestion_function_name" {
  description = "Data ingestion Lambda function name"
  value       = aws_lambda_function.data_ingestion.function_name
}

output "pattern_analysis_function_name" {
  description = "Pattern analysis Lambda function name"
  value       = aws_lambda_function.pattern_analysis.function_name
}

output "api_handler_function_name" {
  description = "API handler Lambda function name"
  value       = aws_lambda_function.api_handler.function_name
}

# ECR repository for Vision Transformer model
output "vision_model_ecr_repository_url" {
  description = "ECR repository URL for Vision Transformer model"
  value       = aws_ecr_repository.vision_model.repository_url
}

output "vision_model_ecr_repository_name" {
  description = "ECR repository name for Vision Transformer model"
  value       = aws_ecr_repository.vision_model.name
}