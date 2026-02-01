import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из файла data/ingredients.json."""
    help = 'Загрузка ингредиентов из json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            required=True,
            help='Путь к файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        file_path = 'data/ingredients.json'

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                ingredients = [
                    Ingredient(
                        name=item['name'].strip(),
                        measurement_unit=item['measurement_unit'].strip()
                    )
                    for item in data
                ]
                Ingredient.objects.bulk_create(
                    ingredients,
                    ignore_conflicts=True
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Загружено {len(ingredients)} ингредиентов'
                    )
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR
                (
                    f'Файл {file_path} содержит некорректный JSON')
            )
