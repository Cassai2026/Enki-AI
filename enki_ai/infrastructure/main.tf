resource "google_container_cluster" "enki_sovereign_cluster" {
  name     = "enki-sovereign-cluster"
  location = "europe-west1" # Low-latency for Stretford
  enable_autopilot = true

  # Enterprise Security: Private Cluster
  private_cluster_config {
    enable_private_nodes    = true
    master_ipv4_cidr_block = "172.16.0.0/28"
  }
}
