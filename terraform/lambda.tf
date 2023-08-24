data "archive_file" "lambda_code" {
    type = "zip"
    source_dir = "./*.py"
    output_path = "./lambda_code.zip"
  }

resource "aws_lambda_function" "aws_lambda_resource" {
    name = "deploy-aws-lambda-image"
    runtime = "python3.8"
    handler = "index.handler"
    code = data.archive_file.lambda_code.output_path
  }

resource "aws_iam_role" "lambda_role" {
  name = "deploy-aws-lambda-image-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_policy_attachment" {
  name       = "deploy-aws-lambda-image-policy-attachment"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  
  roles = [aws_iam_role.lambda_role.name]
}