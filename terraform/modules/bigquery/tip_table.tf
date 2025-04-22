resource "google_bigquery_table" "tip" {
  dataset_id = google_bigquery_dataset.yelp_dataset.dataset_id
  table_id   = "tip"

  schema = file("${path.module}/schemas/tip_schema.json")
  deletion_protection = false

  labels = {
    env = var.env
  }
}