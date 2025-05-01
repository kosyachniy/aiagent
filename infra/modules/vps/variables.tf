
variable "name" {
  description = "Имя VPS"
  type        = string
}

variable "region" {
  description = "Регион для VPS"
  type        = string
  default     = "fra1"
}

variable "size" {
  description = "Размер VPS"
  type        = string
  default     = "s-1vcpu-1gb"
}

variable "image" {
  description = "Образ для VPS"
  type        = string
  default     = "ubuntu-24-04-x64"
}

variable "ssh_keys" {
  description = "Список SSH ключей (ID) для доступа"
  type        = list(string)
  default     = []
}

variable "user_data" {
  description = "User data для инициализации VPS (cloud-init)"
  type        = string
  default     = ""
}
