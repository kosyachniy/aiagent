// Создание VPC сети для инфраструктуры AI Planner на DigitalOcean

// CIDR блок для VPC (можно переопределить в root variables или tfvars)
variable "vpc_ip_range" {
  description = "CIDR-блок для VPC сети"
  type        = string
  default     = "10.10.0.0/16"
}

// Ресурс VPC
resource "digitalocean_vpc" "main" {
  name        = "${var.vps_name}-vpc"
  region      = var.vps_region
  ip_range    = var.vpc_ip_range
  description = "VPC сеть для AI Planner инфраструктуры"
}

// Вывод VPC ID
output "vpc_id" {
  description = "ID созданной VPC сети"
  value       = digitalocean_vpc.main.id
}

// Вывод VPC IPv4 CIDR
output "vpc_ip_range" {
  description = "CIDR-блок VPC сети"
  value       = digitalocean_vpc.main.ip_range
}
