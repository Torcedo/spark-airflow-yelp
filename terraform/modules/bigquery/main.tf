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