variable "project_id" {
  type        = string
  description = "L'ID de ton projet GCP"
}

variable "region" {
  description = "La région GCP à utiliser"
  type    = string
  default = "europe-west1"
}
