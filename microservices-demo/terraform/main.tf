terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_firewall" "main" {
  name    = "${var.project_name}-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "3000", "9090"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = [var.project_name]
}

resource "google_compute_instance" "main" {
  name         = "${var.project_name}-vm"
  machine_type = var.machine_type
  zone         = var.zone

  tags = [var.project_name]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 30
      type  = "pd-ssd"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.public_key_path)}"
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    set -e

    apt-get update -y
    apt-get install -y ca-certificates curl gnupg lsb-release git unzip

    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu
  EOF

  service_account {
    scopes = ["cloud-platform"]
  }
}
