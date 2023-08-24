variable "aws_region" {
    type = string
    default = "ap-south-1"
}

variable "backend_bucket_name" {
    type = string
    default = "deploy-aws-lambda-image-tf-state"
}

variable "backend_bucket_key_name" {
    type = string
    default = "deploy_lambda.tfstate"
}
