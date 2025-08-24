terraform {
  required_providers {
    google = {
        source = "hashicorp/google"
        version = "~> 4.0"
    }

    google-beta = {
        source  = "hashicorp/google-beta"
        version = "~> 4.0"
    }
  }
}

# Project Data
data "google_project" "current_project" {
    project_id = var.gcp_project_id
}


# Service Account
resource "google_service_account" "databricks" {
  account_id = "databricks-sa"
  display_name = "Databricks Service Account"
  description = "Service account for Databricks workspace"
}

# IAM permissions for service account
resource "google_project_iam_member" "databricks_permissions" {
  for_each = toset([
    "roles/storage.admin",
    "roles/bigquery.admin",
    "roles/databricks.serviceAgent"
  ])

  project = var.gcp_project_id
  role = each.value
  member = "serviceAccount:${google_service_account.databricks.email}"
}

resource "google_compute_network" "databricks_vpc" {
  name = var.network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "databricks_subnet" {
  name = "databricks-subnet"
  ip_cidr_range = "10.0.0.0/16"
  region = var.gcp_region
  network = google_compute_network.databricks_vpc.id
}

# Google Cloud Storage bucket 
resource "google_storage_bucket" "databricks_storage_bucket" {
  name = "${var.gcp_project_id}-databricks-data"
  location = var.gcp_region
  uniform_bucket_level_access = true
  force_destroy = true

  versioning {
    enabled = true
  }
}

# workspace 
resource "google_databricks_workspace" "db_workspace" {
  provider = google-beta

  name =  var.databricks_workspace_name
  location = var.gcp_region
  project = var.gcp_project_id

  network {
    network_name = google_compute_network. databricks_vpc.name
    subnet = google_compute_subnetwork.databricks_subnet.name
  }

  service_account = google_service_account.databricks.email
}