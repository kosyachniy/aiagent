resource "digitalocean_domain_record" "dns_record" {
  domain = var.domain
  type   = var.type
  name   = var.name
  data   = var.value
  ttl    = var.ttl
}
