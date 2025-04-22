resource "google_bigquery_table" "checkin" {
  dataset_id = google_bigquery_dataset.yelp_dataset.dataset_id
  table_id   = "checkin"

  schema = file("${path.module}/schemas/checkin_schema.json")
  deletion_protection = false

  labels = {
    env = var.env
  }
}