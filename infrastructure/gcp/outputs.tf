output "databricks_workspace_url" {
    value = google_databricks_workspace.db_workspace.workspace_url
    description = "Workspace URL"
}

output "databricks_workspace_id" {
    value = google_databricks_workspace.db_workspace.workspace_id
    description = "Workspace ID"
}

output "gcs_bucket" {
    value = google_storage_bucket.databricks_storage_bucket.name
    description = "GCS Bucket Name"
}

output "service_account" {
    value = google_service_account.databricks.email
    description = "Service account email"
}