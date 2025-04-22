resource "google_bigquery_table" "business" {
  dataset_id = google_bigquery_dataset.yelp_dataset.dataset_id
  table_id   = "business"

  schema = file("${path.module}/schemas/business_schema.json")
  deletion_protection = false

  labels = {
    env = var.env
  }

  clustering {
    fields = ["state"]
  }
}
