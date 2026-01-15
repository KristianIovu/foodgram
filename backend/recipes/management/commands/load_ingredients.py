import csv
import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из CSV или JSON файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        path = options['path']

        if not path:
            self.stdout.write(
                self.style.ERROR('Укажите путь к файлу: --path <путь>')
            )
            return

        if path.endswith('.csv'):
            self.load_from_csv(path)
        elif path.endswith('.json'):
            self.load_from_json(path)
        else:
            self.stdout.write(
                self.style.ERROR('Формат файла не поддерживается. Используйте .csv или .json')
            )

    def load_from_csv(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            ingredients = []
            for row in reader:
                if len(row) == 2:
                    name, measurement_unit = row
                    ingredients.append(
                        Ingredient(
                            name=name.strip(),
                            measurement_unit=measurement_unit.strip()
                        )
                    )

            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено {len(ingredients)} ингредиентов из CSV'
                )
            )

    def load_from_json(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            ingredients = []
            for item in data:
                ingredients.append(
                    Ingredient(
                        name=item['name'].strip(),
                        measurement_unit=item['measurement_unit'].strip()
                    )
                )

            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено {len(ingredients)} ингредиентов из JSON'
                )
            )
