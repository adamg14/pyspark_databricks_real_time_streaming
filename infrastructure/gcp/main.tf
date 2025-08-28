# documentation for creating a gcp databricks workspace
# https://registry.terraform.io/providers/databricks/databricks/latest/docs/guides/gcp-workspace
terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"  # Try version 5.x or higher
    }

    databricks = {
      source = "databricks/databricks"
      version = "~> 1.56"
    }
  }
}


provider "google" {
  project = var.gcp_project_id
  region = var.gcp_region
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
data "google_iam_policy" "this" {
  binding {
    role = "roles/iam.serviceAccountTokenCreator"
    members = var.delegate_from
  }
}

resource "google_service_account_iam_policy" "impersonatable" {
  service_account_id = google_service_account.databricks.name
  policy_data = data.google_iam_policy.this.policy_data
}

resource "google_iam_custom_role" "databricks_custom_role" {
  role_id = "databricks_workspace_creator"
  title = "Databricks Workspace Creator"
  permissions = [
    "iam.serviceAccounts.getIamPolicy",
    "iam.serviceAccounts.setIamPolicy",
    "iam.serviceAccounts.create",
    "iam.serviceAccounts.get",
    "iam.roles.create",
    "iam.roles.delete",
    "iam.roles.get",
    "iam.roles.update",
    "resourcemanager.projects.get",
    "resourcemanager.projects.getIamPolicy",
    "resourcemanager.projects.setIamPolicy",
    "serviceusage.services.get",
    "serviceusage.services.list",
    "serviceusage.services.enable",
    "compute.networks.get",
    "compute.networks.updatePolicy",
    "compute.projects.get",
    "compute.subnetworks.get",
    "compute.subnetworks.getIamPolicy",
    "compute.subnetworks.setIamPolicy",
    "compute.firewalls.get",
    "compute.firewalls.create",
  ]
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

# databricks workspace 
resource "databricks_mws_workspaces" "databricks_workspace" {
  account_id = var.account_id
  workspace_name = var.databricks_workspace_name
  location = var.gcp_region
}


resource "google_project_iam_member" "sa2_can_create_workspaces" {
  project = var.gcp_project_id
  role    = google_project_iam_custom_role.workspace_creator.id
  member  = "serviceAccount:${google_service_account.databricks.email}"
}