variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "profile" {
  description = "AWS credentials profile"
  type        = string
  default     = "default"
}

variable "openai_api_key" {
  description = "OpenAI API KEY"
  type        = string
  sensitive   = true
}

variable "cohere_api_key" {
  description = "Cohere API KEY"
  type        = string
  sensitive   = true
}