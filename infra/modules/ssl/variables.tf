variable "digitalocean_token" {
  description = "Token для провайдера DigitalOcean (для DNS-challenge)"
  type        = string
  sensitive   = true
}

variable "email" {
  description = "Email для регистрации в ACME (Let's Encrypt)"
  type        = string
}

variable "domain" {
  description = "Основной домен для сертификата (например, example.com)"
  type        = string
}

variable "additional_names" {
  description = "Список дополнительных доменных имён для SAN"
  type        = list(string)
  default     = []
}

variable "server_url" {
  description = "URL сервера ACME"
  type        = string
  default     = "https://acme-v02.api.letsencrypt.org/directory"
}
