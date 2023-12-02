output "secretsmanager_name" {
  value = aws_secretsmanager_secret.this.name
}

output "secretsmanager_arn" {
  value = aws_secretsmanager_secret.this.arn
}

output "ssm_parameter_name" {
  value = aws_ssm_parameter.this.name
}

output "ssm_parameter_arn" {
  value = aws_ssm_parameter.this.arn
}