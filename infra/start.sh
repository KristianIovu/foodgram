#!/bin/bash

# Wait for database
sleep 10

# Run migrations
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --noinput

# Collect static files
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Load ingredients
docker compose -f docker-compose.prod.yml exec backend python manage.py load_ingredients --path /app/data/ingredients.json

# Create superuser if not exists
docker compose -f docker-compose.prod.yml exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"
