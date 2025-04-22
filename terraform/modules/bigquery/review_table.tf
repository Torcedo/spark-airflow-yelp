resource "google_bigquery_table" "review" {
  dataset_id = google_bigquery_dataset.yelp_dataset.dataset_id
  table_id   = "review"

  schema = file("${path.module}/schemas/review_schema.json")
  deletion_protection = false

  labels = {
    env = var.env
  }
}