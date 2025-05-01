resource "null_resource" "docker_host" {
  triggers = {
    # Перезапуски при изменении env или репозитория
    project_rev = timestamp()
  }

  connection {
    host        = var.host
    user        = var.user
    private_key = var.private_key
  }

  provisioner "remote-exec" {
    inline = [
      # Обновление системы и установка Docker
      "apt-get update -y",
      "apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common git",
      # Добавляем репозиторий Docker и ключ
      "curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo $ID)/gpg | apt-key add -",
      "add-apt-repository \"deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(. /etc/os-release; echo $ID) $(lsb_release -cs) stable\"",
      # Установка Docker Engine
      "apt-get update -y",
      "apt-get install -y docker-ce docker-ce-cli containerd.io",
      "systemctl enable docker",
      "systemctl start docker",

      # Установка Docker Compose
      "curl -L \"https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '\"' -f 4)/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
      "chmod +x /usr/local/bin/docker-compose",

      # Развёртывание приложения
      "mkdir -p /opt/${var.project_name}",
      "if [ -d /opt/${var.project_name}/.git ]; then cd /opt/${var.project_name} && git fetch && git checkout ${var.branch} && git pull; else git clone -b ${var.branch} ${var.repo_url} /opt/${var.project_name}; fi",
      # Запись .env
      "echo '${var.env_contents}' > /opt/${var.project_name}/.env",
      # Запуск Docker Compose
      "cd /opt/${var.project_name} && docker-compose up -d --build"
    ]
  }
}
