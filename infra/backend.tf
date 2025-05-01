terraform {
  # Настройка remote state в S3 (замени параметры на свои)
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "ai-planner/terraform.tfstate"
    region         = "eu-central-1"  # пример: eu-central-1 (Frankfurt)
    encrypt        = true
    dynamodb_table = "terraform-state-lock"  # для блокировок (опционально)
  }
}
