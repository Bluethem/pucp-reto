#!/bin/bash
set -e

echo "→ Ejecutando migraciones..."
alembic upgrade head || echo "→ (migraciones ya ejecutadas)"

echo "→ Sembrando datos iniciales si la BD está vacía..."
if [ -f scripts/seed_infobras.py ]; then
    python scripts/seed_infobras.py || echo "→ seed saltado (BD con datos)"
elif [ -f backend/scripts/seed_infobras.py ]; then
    python backend/scripts/seed_infobras.py || echo "→ seed saltado (BD con datos)"
else
    echo "→ scripts/seed_infobras.py no encontrado, saltando..."
fi

echo "→ Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
