output "username" {
  description = "RDS instance root username"
  value       = aws_db_instance.this.username
  sensitive   = true
}

output "address" {
  description = "The hostname of the RDS instance."
  value       = aws_db_instance.this.address
  sensitive   = true
}

output "port" {
  description = "The port of the RDS instance."
  value       = aws_db_instance.this.port
  sensitive   = true
}