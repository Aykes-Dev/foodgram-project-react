from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка тегов'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Загрузка дынных...'))
        data = [
            {'name': 'Завтрак', 'color': '#FF0000', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#33CCFF', 'slug': 'lunche'},
            {'name': 'Ужин', 'color': '#FF77FF', 'slug': 'dinner'},
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Тэги загружены'))
