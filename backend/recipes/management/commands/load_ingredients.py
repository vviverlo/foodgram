import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из data/ingredients.json в БД'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help=(
                'Путь к JSON (по умолчанию: '
                '<корень репозитория>/data/ingredients.json)'
            ),
        )

    def handle(self, *args, **options):
        if options['path']:
            path = Path(options['path'])
        else:
            # В образе бэкенда есть только /app — файл кладём в backend/data/.
            # При запуске из клона репозитория сработает ../data (корень репо).
            path = Path(settings.BASE_DIR) / 'data' / 'ingredients.json'
            if not path.is_file():
                alt = (
                    Path(settings.BASE_DIR).parent
                    / 'data'
                    / 'ingredients.json'
                )
                if alt.is_file():
                    path = alt

        if not path.is_file():
            self.stderr.write(self.style.ERROR(f'Файл не найден: {path}'))
            return

        with path.open(encoding='utf-8') as f:
            items = json.load(f)

        unique = {}
        for row in items:
            name = row['name'].strip()
            unit = row['measurement_unit'].strip()
            unique[(name, unit)] = Ingredient(name=name, measurement_unit=unit)

        to_create = list(unique.values())
        before = Ingredient.objects.count()
        Ingredient.objects.bulk_create(to_create, ignore_conflicts=True)
        after = Ingredient.objects.count()
        created = after - before
        skipped = len(to_create) - created

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово: создано {created}, уже были в БД {skipped}, '
                f'всего строк в файле {len(items)}.'
            )
        )
