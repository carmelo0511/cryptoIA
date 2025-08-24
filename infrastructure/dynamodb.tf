# DynamoDB table for pattern caching
resource "aws_dynamodb_table" "pattern_cache" {
  name         = "${var.project_name}-pattern-cache-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "symbol"
  range_key    = "timestamp"

  attribute {
    name = "symbol"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = local.common_tags
}

# DynamoDB table for market data
resource "aws_dynamodb_table" "market_data" {
  name         = "${var.project_name}-market-data-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "symbol"
  range_key    = "timestamp"

  attribute {
    name = "symbol"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = local.common_tags
}

# DynamoDB table for model predictions
resource "aws_dynamodb_table" "predictions" {
  name         = "${var.project_name}-predictions-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "prediction_id"

  attribute {
    name = "prediction_id"
    type = "S"
  }

  attribute {
    name = "symbol"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "N"
  }

  global_secondary_index {
    name            = "symbol-created_at-index"
    hash_key        = "symbol"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = local.common_tags
}