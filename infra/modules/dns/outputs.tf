output "record_id" {
  description = "ID созданной DNS-записи"
  value       = digitalocean_domain_record.dns_record.id
}

output "fqdn" {
  description = "Полное доменное имя для записи"
  value       = "${var.name == "@" ? var.domain : "${var.name}.${var.domain}"}"
}

output "record_type" {
  description = "Тип DNS-записи"
  value       = digitalocean_domain_record.dns_record.type
}

output "record_value" {
  description = "Значение DNS-записи"
  value       = digitalocean_domain_record.dns_record.data
}
