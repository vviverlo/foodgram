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

        created, skipped = 0, 0
        for row in items:
            name = row['name'].strip()
            unit = row['measurement_unit'].strip()
            obj, was_created = Ingredient.objects.get_or_create(
                name=name,
                measurement_unit=unit,
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово: создано {created}, уже были в БД {skipped}, '
                f'всего строк в файле {len(items)}.'
            )
        )
