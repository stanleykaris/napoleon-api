#!/bin/sh

set -e

# Wait for the database to be ready
python manage.py wait_for_db

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
cat << EOF | python manage.py shell
import os
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME')).exists():
    User.objects.create_superuser(
        os.environ.get('DJANGO_SUPERUSER_USERNAME'),
        os.environ.get('DJANGO_SUPERUSER_EMAIL'),
        os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Seed the database with initial data
echo "Seeding database..."
python manage.py seed_data

# Start the application
exec "$@"
