#!/bin/bash
# Production startup script for Sentry Backend
# This script runs database migrations and creates initial data

set -e  # Exit on any error

echo "🚀 Starting Sentry Backend Production Setup..."

# Change to the sentry directory where manage.py is located
cd /app/sentry || exit 1

echo "📦 Running makemigrations..."
python manage.py makemigrations || echo "ℹ️  No new migrations to create"

echo "🔄 Running migrations..."
python manage.py migrate

echo "👤 Creating initial data (superuser)..."
python manage.py create_initial_data

echo "✅ Production setup complete!"
echo "🌐 Starting Gunicorn server..."

# Start Gunicorn with production settings
# -w: number of worker processes (2 * CPU cores + 1 is recommended)
# -b: bind address
# --timeout: worker timeout in seconds
# --access-logfile: access log file (use - for stdout)
# --error-logfile: error log file (use - for stderr)
# --capture-output: capture stdout/stderr
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --log-level info \
    sentry.wsgi:application

