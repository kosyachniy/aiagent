output "deploy_trigger" {
  description = "Триггер последней операции деплоя (метка времени)"
  value       = null_resource.docker_host.triggers.project_rev
}
