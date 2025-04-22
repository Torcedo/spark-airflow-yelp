variable "project_id" {
  description = "L'identifiant du projet GCP"
  type        = string
}

variable "region" {
  description = "Région par défaut"
  type        = string
}

variable "env" {
  description = "Environnement (dev, prod, etc.)"
  type        = string
}
