from django.core.management.base import BaseCommand
from recipes.models import Tag

DEFAULT_TAGS = (
    ('Завтрак', 'breakfast'),
    ('Обед', 'lunch'),
    ('Ужин', 'dinner'),
)


class Command(BaseCommand):
    help = 'Создаёт базовые теги, если их ещё нет'

    def handle(self, *args, **options):
        created = 0
        for name, slug in DEFAULT_TAGS:
            _obj, was_created = Tag.objects.get_or_create(
                slug=slug,
                defaults={'name': name},
            )
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Теги: создано новых {created}, '
                f'всего в БД {Tag.objects.count()}.'
            )
        )
