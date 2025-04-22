resource "google_composer_environment" "composer_env" {
  name   = "${var.project_id}-composer"
  region = var.region

  config {
    software_config {
      image_version = "composer-3-airflow-2.10.5"

    env_variables = {
    DATAPROC_CLUSTER    = "${var.project_id}-dataproc"
    BUCKET_RAW          = var.bucket_raw
    BUCKET_INTERMEDIATE = var.bucket_intermediate
    BUCKET_SCRIPTS      = var.bucket_scripts
    }

    }
  }
}