resource "google_storage_bucket" "yelp_raw" {
  name                        = "${var.project_id}-yelp-raw"
  location                    = "EU"
  force_destroy               = true
  uniform_bucket_level_access = true
  storage_class               = "STANDARD"

  versioning {
    enabled = true
  }

  labels = {
    env    = "dev"
    source = "terraform"
  }
}
resource "google_storage_bucket" "yelp_intermediate" {
  name                        = "${var.project_id}-yelp-intermediate"
  location                    = "EU"
  force_destroy               = true
  uniform_bucket_level_access = true
  storage_class               = "STANDARD"

  versioning {
    enabled = true
  }

  labels = {
    env    = "dev"
    source = "terraform"
    usage  = "intermediate"
  }
}


resource "google_storage_bucket" "spark_scripts" {
  name     = "${var.project_id}-spark-scripts"
  location = "EU"
  force_destroy = true
  uniform_bucket_level_access = true
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  labels = {
    env    = "dev"
    source = "terraform"
    usage  = "spark-scripts"
  }
}