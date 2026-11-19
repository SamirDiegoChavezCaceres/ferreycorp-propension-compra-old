# Created only once image_tag is set (after the image is built and pushed to
# the Artifact Registry repo above) - see README.md in this folder for the
# two-phase apply this chicken-and-egg dependency requires.
resource "google_cloud_run_v2_service" "api" {
  count    = var.image_tag == "" ? 0 : 1
  project  = var.project_id
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  # Demo/sandbox resource, torn down after the interview - allow terraform
  # destroy without a manual override.
  deletion_protection = false

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    containers {
      image = var.image_tag
      resources {
        limits = {
          # 512Mi was not enough: pandas+scikit-learn+scipy import alone gets
          # OOM-killed before the container can bind the port, so Cloud Run's
          # health check times out with no error in the app logs.
          cpu    = "1"
          memory = "2Gi"
        }
      }
      ports {
        container_port = 8080
      }
      startup_probe {
        http_get {
          path = "/"
        }
        initial_delay_seconds = 5
        timeout_seconds       = 5
        period_seconds        = 5
        failure_threshold     = 6
      }
    }
  }

  depends_on = [google_project_service.run, google_artifact_registry_repository.repo]
}

# Public, unauthenticated access. This project has no org (personal account),
# so no iam.allowedPolicyMemberDomains constraint blocks allUsers here - unlike
# the waykitech.com-org project this was first tried on (see DECISIONS_LOG /
# README for that story and why a PythonAnywhere-proxy workaround was dropped
# once this project was available instead).
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.image_tag == "" ? 0 : 1
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api[0].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
