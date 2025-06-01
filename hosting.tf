locals {
  safe_use_case = replace(var.use_case, "_", "-")
}

resource "aws_s3_bucket" "voice_app_hosting" {
  bucket = "kaizen-voice-app-${var.station_name}-${local.safe_use_case}-${var.environment}"
  force_destroy = true

  tags = {
    Name      = "KaizenVoiceAppHosting"
    Station   = var.station_name
    UseCase   = var.use_case
    ManagedBy = "Terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "block_public_access" {
  bucket = aws_s3_bucket.voice_app_hosting.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_policy" {
  bucket = aws_s3_bucket.voice_app_hosting.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = "*",
      Action = ["s3:GetObject"],
      Resource = "${aws_s3_bucket.voice_app_hosting.arn}/*"
    }]
  })
}

resource "aws_s3_bucket_website_configuration" "site_config" {
  bucket = aws_s3_bucket.voice_app_hosting.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_object" "index_html" {
  bucket = aws_s3_bucket.voice_app_hosting.id
  key    = "index.html"
  source = "${path.module}/frontend/index.html"
  content_type = "text/html"
}

output "frontend_url" {
  value = "http://${aws_s3_bucket.voice_app_hosting.bucket}.s3-website-${var.aws_region}.amazonaws.com"
}
