locals {
  name   = "eve-project"
  region = var.region

  cluster_version = "1.28"

  vpc_cidr = "10.0.0.0/16"
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)

  tags = {
    managedBy  = "terraform"
    Blueprint  = local.name
    GithubRepo = "github.com/justingodden/eve-project/terraform"
  }
}

resource "random_id" "s3" {
  byte_length = 8
}

resource "random_id" "secrets_manager" {
  byte_length = 8
}

resource "random_password" "rds" {
  length  = 16
  special = false
  # override_special = "!?$"
}

locals {
  rds_login = {
    db_name  = "eve"
    password = random_password.rds.result
    username = "postgres"
    port     = 5432
  }
}