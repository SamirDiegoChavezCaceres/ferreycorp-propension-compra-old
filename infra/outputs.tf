output "artifact_registry_url" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repo_name}"
  description = "Push images here, e.g. docker push <this>/app:v1"
}

output "service_url" {
  value       = var.image_tag == "" ? null : google_cloud_run_v2_service.api[0].uri
  description = "Public URL of the deployed demo API (null until image_tag is set)."
}
