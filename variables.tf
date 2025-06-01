variable "aws_region" {
  description = "AWS region to deploy into"
  default     = "eu-central-1"
}

variable "station_name" {
  description = "Name of the station (e.g., dresden)"
  default     = "dresden"
}

variable "use_case" {
  description = "Use case for this deployment (e.g., success_story)"
  default     = "success_story"
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  default     = "dev"
}
