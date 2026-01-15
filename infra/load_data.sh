#!/bin/bash
echo "Ожидаем запуска базы данных и бэкенда..."
sleep 15

echo "Загружаем ингредиенты..."
docker compose exec backend python manage.py load_ingredients --path /app/data/ingredients.json

echo "Создаем суперпользователя..."
docker compose exec backend python manage.py shell -c "
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
    print('Суперпользователь создан')
else:
    print('Суперпользователь уже существует')
"

echo "Создаем тестовые теги..."
docker compose exec backend python manage.py shell -c "
from recipes.models import Tag
tags = [
    {'name': 'Завтрак', 'color': '#FFA500', 'slug': 'breakfast'},
    {'name': 'Обед', 'color': '#32CD32', 'slug': 'lunch'},
    {'name': 'Ужин', 'color': '#4169E1', 'slug': 'dinner'},
]
for tag_data in tags:
    Tag.objects.get_or_create(**tag_data)
print('Теги созданы')
"

echo "Готово! Приложение доступно по http://localhost"
