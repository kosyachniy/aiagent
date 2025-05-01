output "certificate_pem" {
  description = "Сгенерированный сертификат в PEM формате (chain+cert)"
  value       = acme_certificate.cert.certificate_pem
  sensitive   = true
}

output "private_key_pem" {
  description = "Приватный ключ сертификата в PEM формате"
  value       = tls_private_key.cert_key.private_key_pem
  sensitive   = true
}

output "expiration_time" {
  description = "Дата и время истечения сертификата"
  value       = acme_certificate.cert.certificate_not_after
}
