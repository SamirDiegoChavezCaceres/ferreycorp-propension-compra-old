resource "google_artifact_registry_repository" "repo" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repo_name
  description   = "Docker images for the Ferreycorp propension-de-compra demo API."
  format        = "DOCKER"

  depends_on = [google_project_service.artifact_registry]
}
