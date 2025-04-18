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

resource "google_bigquery_dataset" "yelp_dataset" {
  dataset_id                  = "yelp"
  friendly_name               = "Yelp Dataset"
  description                 = "Dataset Yelp destiné à recevoir les tables transformées depuis Dataproc"
  location                    = var.region
  delete_contents_on_destroy = true

  labels = {
    env    = "dev"
    source = "terraform"
  }
}
