# CloudWatch Events rule for data ingestion
resource "aws_cloudwatch_event_rule" "data_ingestion_schedule" {
  name                = "${var.project_name}-data-ingestion-schedule-${var.environment}"
  description         = "Trigger data ingestion Lambda every 5 minutes"
  schedule_expression = "rate(5 minutes)"
  tags                = local.common_tags
}

# CloudWatch Events target for data ingestion Lambda
resource "aws_cloudwatch_event_target" "data_ingestion_target" {
  rule      = aws_cloudwatch_event_rule.data_ingestion_schedule.name
  target_id = "DataIngestionLambdaTarget"
  arn       = aws_lambda_function.data_ingestion.arn
}

# Permission for CloudWatch Events to invoke Lambda
resource "aws_lambda_permission" "allow_cloudwatch_data_ingestion" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_ingestion.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.data_ingestion_schedule.arn
}