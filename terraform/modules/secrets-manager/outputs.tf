output "secret-name" {
  value = var.name
}

output "arn" {
  value = aws_secretsmanager_secret.this.arn
}