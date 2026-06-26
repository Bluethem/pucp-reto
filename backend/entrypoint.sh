#!/bin/bash
set -e

# Ignorar DATABASE_URL del .env local (usar la de Render)
unset DATABASE_URL

echo "→ Ejecutando migraciones..."
alembic upgrade head

echo "→ Sembrando datos iniciales si la BD está vacía..."
python scripts/seed_infobras.py

echo "→ Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
