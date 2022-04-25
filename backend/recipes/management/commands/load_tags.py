from csv import reader

from django.core.management.base import BaseCommand

from recipes.models import Tag  # isort:skip


class Command(BaseCommand):
    """
    Добавляем теги из файла CSV.
    После миграции БД запускаем командой
    python manage.py load_tags локально
    или
    sudo docker-compose exec backend python manage.py load_tags
    на удаленном сервере.
    Создает записи в модели Tag из списка.
    """
    help = 'Load tags data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipes/data/recipes_tag.csv', 'r',
                encoding='UTF-8'
        ) as tags:
            for row in reader(tags):
                if len(row) == 3:
                    Tag.objects.get_or_create(
                        name=row[0], color=row[1], slug=row[2],
                    )
