# Модуль для создания VPS на DigitalOcean
resource "digitalocean_droplet" "vps" {
  name      = var.name
  region    = var.region
  size      = var.size
  image     = var.image
  ssh_keys  = var.ssh_keys
  user_data = var.user_data
}

resource "digitalocean_floating_ip" "vps_ip" {
  region     = var.region
  droplet_id = digitalocean_droplet.vps.id
}
