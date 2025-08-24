# API Gateway REST API
resource "aws_api_gateway_rest_api" "crypto_api" {
  name = "${var.project_name}-api-${var.environment}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.common_tags
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "crypto_api" {
  rest_api_id = aws_api_gateway_rest_api.crypto_api.id

  depends_on = [
    aws_api_gateway_method.predictions_get,
    aws_api_gateway_method.predictions_post,
    aws_api_gateway_method.patterns_get,
    aws_api_gateway_integration.predictions_get,
    aws_api_gateway_integration.predictions_post,
    aws_api_gateway_integration.patterns_get
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway stage
resource "aws_api_gateway_stage" "crypto_api" {
  deployment_id = aws_api_gateway_deployment.crypto_api.id
  rest_api_id   = aws_api_gateway_rest_api.crypto_api.id
  stage_name    = var.environment

  cache_cluster_enabled = true
  cache_cluster_size    = "0.5"

  tags = local.common_tags
}

# Enable caching for 5 minutes
resource "aws_api_gateway_method_settings" "crypto_api" {
  rest_api_id = aws_api_gateway_rest_api.crypto_api.id
  stage_name  = aws_api_gateway_stage.crypto_api.stage_name
  method_path = "*/*"

  settings {
    caching_enabled      = true
    cache_ttl_in_seconds = 300 # 5 minutes
  }
}

# CORS configuration
resource "aws_api_gateway_method" "cors_options" {
  rest_api_id   = aws_api_gateway_rest_api.crypto_api.id
  resource_id   = aws_api_gateway_rest_api.crypto_api.root_resource_id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cors_options" {
  rest_api_id = aws_api_gateway_rest_api.crypto_api.id
  resource_id = aws_api_gateway_rest_api.crypto_api.root_resource_id
  http_method = aws_api_gateway_method.cors_options.http_method
  type        = "MOCK"
}

# /predictions resource
resource "aws_api_gateway_resource" "predictions" {
  rest_api_id = aws_api_gateway_rest_api.crypto_api.id
  parent_id   = aws_api_gateway_rest_api.crypto_api.root_resource_id
  path_part   = "predictions"
}

# GET /predictions
resource "aws_api_gateway_method" "predictions_get" {
  rest_api_id   = aws_api_gateway_rest_api.crypto_api.id
  resource_id   = aws_api_gateway_resource.predictions.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.symbol" = false
  }
}

resource "aws_api_gateway_integration" "predictions_get" {
  rest_api_id             = aws_api_gateway_rest_api.crypto_api.id
  resource_id             = aws_api_gateway_resource.predictions.id
  http_method             = aws_api_gateway_method.predictions_get.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.api_handler.invoke_arn
}

# POST /predictions
resource "aws_api_gateway_method" "predictions_post" {
  rest_api_id   = aws_api_gateway_rest_api.crypto_api.id
  resource_id   = aws_api_gateway_resource.predictions.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "predictions_post" {
  rest_api_id             = aws_api_gateway_rest_api.crypto_api.id
  resource_id             = aws_api_gateway_resource.predictions.id
  http_method             = aws_api_gateway_method.predictions_post.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.api_handler.invoke_arn
}

# /patterns resource
resource "aws_api_gateway_resource" "patterns" {
  rest_api_id = aws_api_gateway_rest_api.crypto_api.id
  parent_id   = aws_api_gateway_rest_api.crypto_api.root_resource_id
  path_part   = "patterns"
}

# GET /patterns
resource "aws_api_gateway_method" "patterns_get" {
  rest_api_id   = aws_api_gateway_rest_api.crypto_api.id
  resource_id   = aws_api_gateway_resource.patterns.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.symbol" = true
  }
}

resource "aws_api_gateway_integration" "patterns_get" {
  rest_api_id             = aws_api_gateway_rest_api.crypto_api.id
  resource_id             = aws_api_gateway_resource.patterns.id
  http_method             = aws_api_gateway_method.patterns_get.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.api_handler.invoke_arn
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.crypto_api.execution_arn}/*/*"
}