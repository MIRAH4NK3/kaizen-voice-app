data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

data "archive_file" "status_handler_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/status_handler.py"
  output_path = "${path.module}/functions/status_handler.zip"
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "kaizen_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name = "kaizen_lambda_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan",
          "dynamodb:GetItem"
        ],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "s3:PutObject",
          "s3:GetObject"
        ],
        Resource = "arn:aws:s3:::kaizen-voice-raw-dresden/*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_lambda_function" "kaizen_story_handler" {
  function_name = "kaizen_${var.use_case}_${var.station_name}_${var.environment}"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.kaizen_logs.name
    }
  }
}

resource "aws_lambda_function" "transcription_handler" {
  function_name = "kaizen_transcription_handler"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "transcription_handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

resource "aws_lambda_function" "status_handler" {
  function_name = "kaizen_status_handler"
  filename         = data.archive_file.status_handler_zip.output_path
  source_code_hash = data.archive_file.status_handler_zip.output_base64sha256
  handler          = "status_handler.lambda_handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_exec_role.arn
  memory_size      = 128
  timeout          = 10

  environment {
    variables = {
      TABLE_NAME = "kaizen_success_story_dresden_dev"
    }
  }
}

resource "aws_cloudwatch_log_group" "transcription_handler_logs" {
  name              = "/aws/lambda/kaizen_transcription_handler"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "status_handler_logs" {
  name              = "/aws/lambda/kaizen_status_handler"
  retention_in_days = 7
}
