import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from literature.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из файла data/ingredients.csv'

    def handle(self, *args, **kwargs):
        file_path = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.csv'

        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f'❌ Файл не найден: {file_path}'))
            return

        count = 0
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 2:
                    continue
                name, unit = row[0].strip(), row[1].strip()
                _, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=unit
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(
            f'✅ Импортировано {count} ингредиентов из {file_path}'))
