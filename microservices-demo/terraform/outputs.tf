output "public_ip" {
  description = "Public IP of the VM"
  value       = google_compute_instance.main.network_interface[0].access_config[0].nat_ip
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${google_compute_instance.main.network_interface[0].access_config[0].nat_ip}"
}

output "app_url" {
  description = "Main application URL"
  value       = "http://${google_compute_instance.main.network_interface[0].access_config[0].nat_ip}"
}

output "grafana_url" {
  description = "Grafana URL"
  value       = "http://${google_compute_instance.main.network_interface[0].access_config[0].nat_ip}:3000"
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = "http://${google_compute_instance.main.network_interface[0].access_config[0].nat_ip}:9090"
}
