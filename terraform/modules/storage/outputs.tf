output "bucket_yelp_raw_name" {
  value = google_storage_bucket.yelp_raw.name
}

output "bucket_yelp_intermediate_name" {
  value = google_storage_bucket.yelp_intermediate.name
}

output "bucket_spark_scripts_name" {
  value = google_storage_bucket.spark_scripts.name
}
