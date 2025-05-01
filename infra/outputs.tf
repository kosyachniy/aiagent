// Сборные выходные переменные для всей инфраструктуры

// VPC
output "vpc_id" {
  description = "ID VPC сети"
  value       = digitalocean_vpc.main.id
}

// VPS
output "droplet_id" {
  description = "ID созданного дроплета"
  value       = module.vps.droplet_id
}

output "vps_ipv4_address" {
  description = "Основной IPv4 адрес дроплета"
  value       = module.vps.vps_ipv4_address
}

output "floating_ip" {
  description = "Плавающий IP дроплета"
  value       = module.vps.floating_ip
}

// DNS
output "dns_record_id" {
  description = "ID созданной DNS-записи"
  value       = module.dns.record_id
}

output "dns_fqdn" {
  description = "Полное доменное имя для записи"
  value       = module.dns.fqdn
}

// SSL
output "certificate_pem" {
  description = "Сгенерированный SSL-сертификат (chain+cert)"
  value       = module.ssl.certificate_pem
  sensitive   = true
}

output "private_key_pem" {
  description = "Приватный ключ SSL-сертификата"
  value       = module.ssl.private_key_pem
  sensitive   = true
}

output "certificate_expiration" {
  description = "Дата и время истечения сертификата"
  value       = module.ssl.expiration_time
}

// Deployment trigger
output "deploy_trigger" {
  description = "Триггер последнего деплоя приложения"
  value       = module.docker_host.deploy_trigger
}
