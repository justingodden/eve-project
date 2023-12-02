resource "aws_secretsmanager_secret" "this" {
  name = var.add_suffix ? "${var.name}-${random_id.secrets_manager.hex}" : var.name
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id     = aws_secretsmanager_secret.this.id
  secret_string = jsonencode(var.secrets)
}

resource "aws_ssm_parameter" "this" {
  name  = "/${var.name}/secret-name"
  type  = "String"
  value = aws_secretsmanager_secret.this.name
}