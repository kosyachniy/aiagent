variable "domain" {
  description = "Основной домен для управления DNS-записями"
  type        = string
}

variable "name" {
  description = "Имя DNS-записи (например, 'www' или '@')"
  type        = string
}

variable "type" {
  description = "Тип записи (A, AAAA, CNAME, TXT, MX и т.п.)"
  type        = string
  default     = "A"
}

variable "value" {
  description = "Значение DNS-записи (IP-адрес для A, целевой хост для CNAME и т.д.)"
  type        = string
}

variable "ttl" {
  description = "Time-to-live записи в секундах"
  type        = number
  default     = 3600
}
