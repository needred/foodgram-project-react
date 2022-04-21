from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .fields import HexColorField

User = get_user_model()


class Tag(models.Model):
    """
    Модель тегов.
    name - название тега
    color - HEX-код цвета
    slug - идентификатор в URL.
    """
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=40,
        unique=True,
        null=False,
        help_text='Название тега',
    )
    color = HexColorField(
        verbose_name=_('HEX-код цвета'),
        unique=True,
        null=True,
        help_text='Выберите цвет',
    )
    slug = models.SlugField(
        verbose_name=_('Адрес'),
        unique=True,
        help_text='Придумайте уникальный URL адрес для тега',
    )
    REQUIRED_FIELDS = ('name', 'color', 'slug')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиентов.
    name - название ингредиента
    measurement_unit - единица измерения.
    """
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=200,
        blank=False,
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        verbose_name=_('Единица измерения'),
        max_length=50,
        blank=False,
        help_text='Выберите единицу измерения',
    )
    REQUIRED_FIELDS = ('name', 'measurement_unit')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='pair_unique'),
        )
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецептов.
    name - название рецепта
    author - автор
    text - описание
    tags - теги
    ingredients - ингредиенты
    image - картинка
    cooking_time - время приготовления.
    """
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=200,
        unique=True,
        help_text='Укажите название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор рецепта'),
        help_text='Автор рецепта',
    )
    text = models.TextField(verbose_name=_('Описание'))
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        verbose_name=_('Теги'),
        related_name='recipes',
        help_text='Выберите теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name=_('Ингредиенты рецепта'),
        related_name='recipes',
        help_text='Выберите ингредиенты',
    )
    image = models.ImageField(
        verbose_name='Фото готового блюда',
        upload_to='recipes/',
        help_text='Загрузите изображение с фотографией готового блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите время больше нуля!',
        ),),
        verbose_name=_('Время приготовления'),
        help_text='Задайте время приготовления блюда',
    )

    REQUIRED_FIELDS = '__all__'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTags(models.Model):
    """
    Модель тегов в рецептах.
    recipe - рецепт
    tag - тег.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name=_('Тег'),
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='recipe_tag_exists',
            ),
        )
        verbose_name = 'Тег в рецепте'
        verbose_name_plural = 'Теги в рецепте'

    def __str__(self):
        return self.tag.name


class RecipeIngredients(models.Model):
    """
    Модель ингредиентов в рецептах.
    recipe - рецепт
    ingredient - ингредиент
    amount - количество.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name=_('Рецепт'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='ingredient_recipe',
        verbose_name=_('Ингредиент'),
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество больше нуля!',
        ),),
        verbose_name=_('Количество'),
        help_text='Введите количество единиц ингредиента',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='recipe_ingredient_exists'),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1'),
        )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} – {self.amount}'


class FavoriteRecipe(models.Model):
    """
    Модель избранных рецептов.
    recipe - рецепт
    user - пользователь, добавивший рецепт в избранное.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        related_name='in_favorite',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='favorite',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном пользователя {self.user}'


class ShoppingList(models.Model):
    """
    Модель списка покупок.
    recipe - рецепт
    user - пользователь.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        related_name='shopping_recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='shopping_user',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='shopping_recipe_user_exists',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} у пользователя {self.user}'
