module "storage" {
  source     = "./modules/storage"
  project_id = var.project_id
  region     = var.region
  env        = var.env
}

module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  region     = var.region
  env        = var.env
}

module "dataproc" {
  source     = "./modules/dataproc"
  project_id = var.project_id
  region     = var.region
  env        = var.env
}

module "composer" {
  source     = "./modules/composer"
  project_id = var.project_id
  region     = var.region
  env        = var.env

  # noms des buckets storage
  bucket_raw          = module.storage.bucket_yelp_raw_name
  bucket_intermediate = module.storage.bucket_yelp_intermediate_name
  bucket_scripts      = module.storage.bucket_spark_scripts_name
}
