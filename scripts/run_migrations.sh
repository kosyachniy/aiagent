#!/usr/bin/env bash
# Usage: `./scripts/run_migrations.sh`

export MONGO_URI="${MONGO_URI:-mongodb://localhost:27017/aiagent}"
export MONGO_DB_NAME="${MONGO_DB_NAME:-aiagent}"

python - <<'PYCODE'
from migrations.config import migrator
migrator.up()
PYCODE
