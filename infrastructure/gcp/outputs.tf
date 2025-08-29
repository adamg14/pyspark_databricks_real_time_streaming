output "workspace_id" {
    description = "Databricks workspace ID"
    value = databricks_mws_workspaces.this.id
}

output "workspace_url" {
    description = "Databricks URL Workspace"
    value = databricks_mws_workspaces.this.workspace_url
}

output "gcp_workspace_service_account" {
    description = "Serveice account for the databricks workspace created by databricks"
    value = databricks_mws_workspaces.this.gcp_workspace_sa
}