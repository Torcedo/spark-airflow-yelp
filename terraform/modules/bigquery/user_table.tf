resource "google_bigquery_table" "user" {
  dataset_id = google_bigquery_dataset.yelp_dataset.dataset_id
  table_id   = "user"

  schema = file("${path.module}/schemas/user_schema.json")
  deletion_protection = false

  labels = {
    env = var.env
  }
}