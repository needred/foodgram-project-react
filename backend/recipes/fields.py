from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _


class HexColorField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 7)
        super().__init__(*args, **kwargs)
        self.validators.append(
            #    regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            validators.RegexValidator(
                regex=r'#([a-fA-F0-9]{6})',
                message=_('Введите корректное значение HEX кода цвета'),
            )
        )
