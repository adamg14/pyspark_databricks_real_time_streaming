# main.tf
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = ">= 1.86.0"
    }
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = "databricks-workspace-470520"
  region  = "us-central1"
}

# ✅ USE SERVICE ACUTHENTICATION INSTEAD - MORE RELIABLE
provider "databricks" {
  alias      = "mws"
  host       = "https://accounts.gcp.databricks.com"
  account_id = "e3ddc3e5-556a-4c21-b6bc-1aa0844c64b5"
  
  # Method 1: Use service account (RECOMMENDED)
  google_service_account = "databricks-terraform@databricks-workspace-470520.iam.gserviceaccount.com"
  google_credentials     = file("databricks-key.json")
  
  # Method 2: OR if you want to use ADC, add this:
  # auth_type = "google-credentials"
}

resource "databricks_mws_workspaces" "this" {
  provider      = databricks.mws
  account_id    = "e3ddc3e5-556a-4c21-b6bc-1aa0844c64b5"
  workspace_name     = "test-workspace-$(date +%s)"  # UNIQUE name with timestamp
  deployment_name    = "test-deployment"
  cloud         = "gcp"
  location      = "us-central1"

  cloud_resource_container {
    gcp {
      project_id = "databricks-workspace-470520"
    }
  }
}