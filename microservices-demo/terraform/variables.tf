
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west3"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "europe-west3-a"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "microservices-demo"
}

variable "machine_type" {
  description = "GCP machine type"
  type        = string
  default     = "e2-medium"
}

variable "public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
