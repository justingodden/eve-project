resource "random_id" "bucket_id" {
  byte_length = 8
}

locals {
  bucket_name = "${var.name}-${random_id.bucket_id.hex}"
}
