# ---------------------------------------------
# API Gateway (HTTP API v2) with CORS enabled
# ---------------------------------------------

resource "aws_apigatewayv2_api" "http_api" {
  name          = "kaizen-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    # Allow your Amplify frontend; replace "*" with your exact domain if desired:
    allow_origins = ["*"]
    # Since you only have a POST /kaizen route today, include POST and OPTIONS
    allow_methods = ["POST", "OPTIONS"]
    # Any headers your frontend will send (e.g., for JSON payloads or Authorization)
    allow_headers = ["Content-Type", "Authorization"]
    # Cache the preflight response for 1 hour (3600 seconds)
    max_age = 3600
  }
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                    = aws_apigatewayv2_api.http_api.id
  integration_type          = "AWS_PROXY"
  integration_uri           = aws_lambda_function.kaizen_story_handler.invoke_arn
  integration_method        = "POST"
  payload_format_version    = "2.0"
}

resource "aws_apigatewayv2_route" "post_kaizen" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /kaizen"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.kaizen_story_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

output "api_url" {
  description = "The HTTP endpoint to submit Kaizen stories"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}
