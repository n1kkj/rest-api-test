#!/bin/bash

echo "Waiting for PostgreSQL port..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Waiting for PostgreSQL to fully initialize..."
sleep 5

# Инициализируем базу данных
echo "Initializing database..."
cd /app && python db_scripts/init_db.py

# Запускаем приложение
echo "Starting application..."
gunicorn main:app --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker
