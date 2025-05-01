# AI Planner

Лёгкий AI-агент для планирования задач через Telegram-бот на основе LangChain & LangGraph, FastAPI и MongoDB. Поддерживает вложенные инициативы → блоки → задачи, переприоритизацию с учётом бизнес-приоритетов, ресурсов и экспорт в Google Sheets.

---

## 📁 Структура репозитория

```
repo-root/
├── infra/                    Terraform-код инфраструктуры
│   ├── backend.tf
│   ├── provider.tf
│   ├── vpc.tf
│   ├── outputs.tf
│   ├── envs/                Настройки для dev/prod
│   └── modules/
│       ├── vps/
│       ├── docker_host/
│       ├── dns/
│       └── ssl/
├── app/                      Основное приложение
│   ├── main.py               FastAPI (+Loguru)
│   ├── api/                  HTTP-эндпоинты (webhook, задачи)
│   ├── services/             TaskManager и AI Agent
│   ├── models/               Pydantic-схемы
│   ├── db/                   MongoDB через Motor
│   ├── integrations/         Google Sheets и Yandex Tracker
│   ├── core/                 Конфиг и логгер
│   └── langchain_graph/      Navigator & Reprioritizer
├── tasks/                    Dramatiq-воркеры
├── worker.py                 Точка входа для worker
├── scripts/                  Вспомогательные утилиты (миграция в Sheets)
├── tests/                    Unit & Integration тесты
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.development
├── .env.production
└── .github/workflows/ci-cd.yml
```

---

## 🛠 Технологии

- **Python 3.11**
- **FastAPI** — HTTP-сервис
- **Dramatiq** + **Redis** — фоновые задачи
- **MongoDB** (Motor) — хранилище задач
- **LangChain & LangGraph** — AI-графы (o4-mini)
- **pygsheets** — экспорт в Google Sheets
- **Loguru** — логирование
- **Docker** + **docker-compose**
- **Terraform** — IaC (DigitalOcean VPC, VPS, DNS, SSL)
- **GitHub Actions** — CI/CD

---

## 🚀 Быстрый старт

### Локально

1. Клонировать репозиторий:
   ```bash
   git clone <repo-url> && cd repo-root
   ```
2. Создать виртуальное окружение и установить зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Запустить Redis:
   ```bash
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```
4. Создать `.env.development` по примеру и заполнить переменные.
5. Запустить API и worker:
   ```bash
   uvicorn app.main:app --reload
   dramatiq tasks.tasks --redis-url redis://localhost:6379
   ```
6. Прокинуть вебхук через ngrok (опционально):
   ```bash
   ngrok http 8000
   ```

### Docker & docker-compose

1. Создать `.env.production` или использовать dev-файл.
2. Поднять сервисы:
   ```bash
   docker-compose up -d --build
   ```

### Terraform (dev/prod)

1. Перейти в `infra/`, инициализировать Terraform backend:
   ```bash
   cd infra
   terraform init
   ```
2. Применить для нужного окружения:
   ```bash
   terraform apply -var-file=envs/development/terraform.tfvars
   ```
3. После создания VPS и DNS, SSH и запустить Docker Host модуль:
   ```bash
   terraform apply -var-file=envs/development/terraform.tfvars
   ```

---

## ⚙️ CI/CD

- GitHub Actions запускает тесты, собирает и пушит Docker-образ.
- При мерже в `main` автоматически деплоит на прод-сервер через SSH.
- Настройте Secrets: `DOCKERHUB_USER`, `DOCKERHUB_TOKEN`, `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`.

---

## 🔧 Тестирование

```bash
pytest --maxfail=1 --disable-warnings -q
```

- **Unit**: `tests/unit`
- **Integration**: `tests/integration`

---

## 🤝 Вклад

1. Форкните репозиторий.
2. Создайте ветку.
3. Сделайте изменения и отправьте PR.

---

*Happy coding!*
