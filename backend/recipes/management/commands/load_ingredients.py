import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из файла data/ingredients.json."""
    help = 'Загрузка ингредиентов из data/ingredients.json'

    def handle(self, *args, **options):
        file_path = '../data/ingredients.json'

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                ingredients = []
                for item in data:
                    ingredients.append(
                        Ingredient(
                            name=item['name'].strip(),
                            measurement_unit=item['measurement_unit'].strip()
                        )
                    )
                Ingredient.objects.bulk_create(ingredients,
                                               ignore_conflicts=True)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Загружено {len(ingredients)} ингредиентов из {file_path}'
                    )
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден.')
            )
