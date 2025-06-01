resource "aws_dynamodb_table" "kaizen_logs" {
  name         = "kaizen_${var.use_case}_${var.station_name}_${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "story_id"
  range_key    = "timestamp"

  attribute {
    name = "story_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    UseCase   = var.use_case
    Station   = var.station_name
    Env       = var.environment
    ManagedBy = "Terraform"
  }
}
