#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}"; do
  sleep 1
done

echo "PostgreSQL is ready!"

echo "Running migrations..."
python manage.py migrate_schemas --shared

echo "Creating superuser in public schema if not exists..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
from django.db import connection

connection.set_schema_to_public()
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
EOF

echo "Starting Django development server..."
exec "$@"
