.PHONY: help dev serve worker migrate set-priority db-shell test lint fmt docker-up docker-down terraform-init terraform-apply

# Default environment file (adjust if needed)
ENV_FILE?=.env.development

# Commands
help:
	@echo "Available commands:"
	@echo "  make dev                 Start FastAPI with reload"
	@echo "  make serve               Start FastAPI without reload"
	@echo "  make worker              Run background worker"
	@echo "  make migrate             Apply MongoDB migrations"
	@echo "  make set-priority MSG=..  Update CEO speech via script"
	@echo "  make db-shell            Open MongoDB shell"
	@echo "  make test                Run tests with pytest"
	@echo "  make lint                Run linting (flake8)"
	@echo "  make fmt                 Format code with black"
	@echo "  make docker-up           Launch services via Docker Compose"
	@echo "  make docker-down         Tear down Docker Compose services"
	@echo "  make terraform-init      Initialize Terraform"
	@echo "  make terraform-apply     Apply Terraform configuration"

# Development server with auto-reload
dev:
	@echo "Using env file: $(ENV_FILE)"
	source $(ENV_FILE) && uvicorn app.main:app --reload

# Production-like serve
serve:
	@echo "Using env file: $(ENV_FILE)"
	source $(ENV_FILE) && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Background worker
worker:
	@echo "Running worker with Redis at $$REDIS_URL"
	source $(ENV_FILE) && export REDIS_URL=$$REDIS_URL && python worker.py

# Run MongoDB migrations
migrate:
	@echo "Applying MongoDB migrations..."
	./scripts/run_migrations.sh

# Update CEO speech
set-priority:
ifndef MSG
	$(error MSG is not set. Usage: make set-priority MSG="Your speech text")
endif
	./scripts/set_business_priority.sh "$(MSG)"

# Open MongoDB shell
db-shell:
	mongosh "$(MONGO_URI)"

# Testing
test:
	pytest --maxfail=1 --disable-warnings -q

# Linting
lint:
	flake8 app tests

# Formatting
fmt:
	black .

# Docker Compose
docker-up:
	docker-compose up -d --build
	docker-compose logs -f

docker-down:
	docker-compose down

# Terraform
terraform-init:
	terraform init

terraform-apply:
	terraform apply -auto-approve
