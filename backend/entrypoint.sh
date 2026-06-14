#!/bin/sh
set -e

echo "[entrypoint] Waiting for postgres..."
until python -c "import psycopg2, os; psycopg2.connect(os.environ['DATABASE_URL'].replace('+psycopg2','')).close()" 2>/dev/null; do
  sleep 1
done
echo "[entrypoint] Postgres ready."

echo "[entrypoint] Running alembic upgrade head..."
alembic upgrade head

echo "[entrypoint] Starting: $*"
exec "$@"
