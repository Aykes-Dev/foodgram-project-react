import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов json'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Загрузка дынных...'))
        with open('data/ingredients.json', encoding='utf-8', ) as file:
            data = json.loads(file.read())
            Ingredient.objects.bulk_create(
                Ingredient(**ingredient) for ingredient in data)
        self.stdout.write(self.style.SUCCESS('Данные загружены.'))
