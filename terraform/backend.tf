provider "aws" {
    region = "ap-south-1"
}

terraform {
    required_version = ">= 1.5.6"
    backend "s3" {
        bucket = "deploy-aws-lambda-image-tf-state"
        key = "deploy_lambda.tfstate"
        region = "ap-south-1"
    }
}