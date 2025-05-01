terraform {
  required_version = ">= 1.0.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = ">= 2.0.0"
    }
    acme = {
      source  = "vancluever/acme"
      version = ">= 1.7.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

provider "acme" {
  server_url = var.server_url
}

provider "tls" {
  # No additional configuration required
}
