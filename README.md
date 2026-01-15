# Foodgram - «Продуктовый помощник»

Foodgram - это веб-приложение для публикации рецептов. Пользователи могут создавать рецепты, добавлять их в избранное, подписываться на других авторов и формировать список покупок.

## Функциональность

- Регистрация и аутентификация пользователей
- Создание, редактирование и удаление рецептов
- Добавление рецептов в избранное
- Подписка на авторов
- Формирование списка покупок
- Фильтрация по тегам
- Пагинация
- Админ-панель

## Технологии

- **Backend:** Django REST Framework
- **Frontend:** React (предоставлен)
- **База данных:** PostgreSQL
- **Контейнеризация:** Docker, Docker Compose
- **Веб-сервер:** Nginx
- **CI/CD:** GitHub Actions

## Локальный запуск

### Бэкенд
```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
