output "eks" {
  description = "EKS Cluster Output Values"
  value       = module.eks
}

output "rds" {
  description = "RDS Output Values"
  value       = module.rds
  sensitive   = true
}

output "s3" {
  description = "S3 Output Values"
  value       = module.s3
}

output "secrets-manager" {
  description = "SecretsManager Output Values"
  value       = module.secrets-manager
}

output "ecr-data-collector" {
  description = "ECR DataCollecter Repo Output Values"
  value       = module.ecr-data-collector
}

output "ecr-summarizer" {
  description = "ECR Summarizer Repo Output Values"
  value       = module.ecr-summarizer
}

output "ecr-frontend" {
  description = "ECR Frontend Repo Output Values"
  value       = module.ecr-frontend
}

output "ecr-backend" {
  description = "ECR Backend Repo Output Values"
  value       = module.ecr-backend
}