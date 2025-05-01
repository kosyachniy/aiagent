terraform {
  required_providers {
    acme = {
      source  = "vancluever/acme"
      version = ">=1.7.0"
    }
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = ">=2.0.0"
    }
  }
}

provider "acme" {
  server_url = var.server_url
}

provider "digitalocean" {
  token = var.digitalocean_token
}

# Генерация приватного ключа для сертификата
resource "tls_private_key" "cert_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Регистрация аккаунта в ACME
resource "acme_registration" "reg" {
  account_key_pem = tls_private_key.cert_key.private_key_pem
  email_address   = var.email
  server_url      = var.server_url
}

# Запрос сертификата с DNS-валидатором DigitalOcean
resource "acme_certificate" "cert" {
  account_key_pem = acme_registration.reg.account_key_pem
  common_name     = var.domain
  subject_alternative_names = var.additional_names

  dns_challenge {
    provider = "digitalocean"
    config = {
      DIGITALOCEAN_TOKEN = var.digitalocean_token
    }
  }

  # Обновлять сертификат за 30 дней до истечения
  lifecycle {
    create_before_destroy = true
  }
}
