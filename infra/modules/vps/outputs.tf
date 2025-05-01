output "droplet_id" {
  description = "ID созданного дроплета"
  value       = digitalocean_droplet.vps.id
}

output "vps_ipv4_address" {
  description = "IPv4 адрес VPS"
  value       = digitalocean_droplet.vps.ipv4_address
}

output "floating_ip" {
  description = "Выделенный плавающий IP"
  value       = digitalocean_floating_ip.vps_ip.ip_address
}
