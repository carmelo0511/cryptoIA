# Lambda function for data ingestion
resource "aws_lambda_function" "data_ingestion" {
  filename      = "../backend/dist/data-ingestion.zip"
  function_name = "${var.project_name}-data-ingestion-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      PATTERN_CACHE_TABLE = aws_dynamodb_table.pattern_cache.name
      MARKET_DATA_TABLE   = aws_dynamodb_table.market_data.name
      CHARTS_BUCKET       = aws_s3_bucket.charts.bucket
      ENVIRONMENT         = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.data_ingestion]
  tags       = local.common_tags
}

# Lambda function for pattern analysis (Vision Transformer Container)
resource "aws_lambda_function" "pattern_analysis" {
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.vision_model.repository_url}:latest"
  function_name = "${var.project_name}-pattern-analysis-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  timeout       = 300
  memory_size   = 3008 # Max memory for ML inference

  environment {
    variables = {
      PATTERN_CACHE_TABLE = aws_dynamodb_table.pattern_cache.name
      PREDICTIONS_TABLE   = aws_dynamodb_table.predictions.name
      CHARTS_BUCKET       = aws_s3_bucket.charts.bucket
      MARKET_DATA_TABLE   = aws_dynamodb_table.market_data.name
      ENVIRONMENT         = var.environment
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.pattern_analysis,
    aws_ecr_repository.vision_model
  ]
  tags = local.common_tags
}

# Lambda function for API endpoints
resource "aws_lambda_function" "api_handler" {
  filename      = "../backend/dist/api-handler.zip"
  function_name = "${var.project_name}-api-handler-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      PATTERN_CACHE_TABLE = aws_dynamodb_table.pattern_cache.name
      MARKET_DATA_TABLE   = aws_dynamodb_table.market_data.name
      PREDICTIONS_TABLE   = aws_dynamodb_table.predictions.name
      CHARTS_BUCKET       = aws_s3_bucket.charts.bucket
      ENVIRONMENT         = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.api_handler]
  tags       = local.common_tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "data_ingestion" {
  name              = "/aws/lambda/${var.project_name}-data-ingestion-${var.environment}"
  retention_in_days = 14
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "pattern_analysis" {
  name              = "/aws/lambda/${var.project_name}-pattern-analysis-${var.environment}"
  retention_in_days = 14
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "api_handler" {
  name              = "/aws/lambda/${var.project_name}-api-handler-${var.environment}"
  retention_in_days = 14
  tags              = local.common_tags
}