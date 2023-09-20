import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов csv'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Загрузка дынных...'))
        with open('data/ingredients.csv', 'r', encoding="utf-8",) as file:
            data = csv.reader(file)
            Ingredient.objects.bulk_create(
                Ingredient(
                    name=name,
                    measurement_unit=measurement_unit)
                for name, measurement_unit in data)
        self.stdout.write(self.style.SUCCESS('Ингредиенты добавлены'))
