variable "host" {
  description = "IP-адрес целевого хоста"
  type        = string
}

variable "user" {
  description = "SSH-пользователь"
  type        = string
  default     = "root"
}

variable "private_key" {
  description = "Приватный SSH-ключ для подключения"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Имя директории проекта на хосте"
  type        = string
}

variable "repo_url" {
  description = "Git-репозиторий с кодом приложения"
  type        = string
}

variable "branch" {
  description = "Ветка репозитория для деплоя"
  type        = string
  default     = "main"
}

variable "env_contents" {
  description = "Содержимое .env файла для приложения"
  type        = string
  sensitive   = true
}
