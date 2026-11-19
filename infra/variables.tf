variable "project_id" {
  description = "GCP project id - personal sandbox under sachavezca@gmail.com, no org policy restrictions."
  type        = string
  default     = "experimentos-512918"
}

variable "region" {
  description = "Region for Artifact Registry and Cloud Run."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name."
  type        = string
  default     = "ferreycorp-propension-demo"
}

variable "repo_name" {
  description = "Artifact Registry Docker repository name."
  type        = string
  default     = "ferreycorp-demo"
}

variable "image_tag" {
  description = "Full image tag to deploy, e.g. <region>-docker.pkg.dev/<project>/<repo>/app:v1. Empty until the image is built and pushed (chicken-and-egg: the registry must exist first)."
  type        = string
  default     = ""
}
