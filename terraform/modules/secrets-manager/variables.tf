variable "name" {
  type = string
}

variable "secrets" {
  type      = map(any)
  sensitive = true
}

variable "add_suffix" {
  type        = bool
  description = "Add hex value to secret name"
}