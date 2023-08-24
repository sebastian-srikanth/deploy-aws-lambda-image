provider "aws" {
    region = var.aws_region
}

terraform {
    required_version = ">= 1.0.9"
    backend "s3" {
        bucket = var.backend_bucket_name
        key = var.backend_bucket_key_name
        region = var.aws_region
    }
}