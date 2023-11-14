variable "name" {
  type = string
}

variable "secrets" {
  type      = map(any)
  sensitive = true
}