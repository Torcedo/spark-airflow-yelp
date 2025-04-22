
resource "google_dataproc_cluster" "dataproc_cluster" {
  name   = "${var.project_id}-dataproc"
  region = var.region

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = "e2-standard-4" 
      disk_config {
        boot_disk_size_gb = 50
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "e2-standard-2"
      disk_config {
        boot_disk_size_gb = 50
      }
    }

    gce_cluster_config {
      zone = "${var.region}-b"
    }

    software_config {
      image_version = "2.1-debian11"  # stable avec PySpark
    }
  }

  labels = {
    env = "dev"
  }
}