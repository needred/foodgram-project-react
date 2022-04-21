from django.contrib.auth import get_user_model
from django.db.models import F
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import CustomUserSerializer  # isort:skip

from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingList,
    Tag
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода тэгов.
    """
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class ShowIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода ингредиентов в рецепте.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов.
    """
    class Meta:
        model = Recipe
        fields = '__all__'


class ShowRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода данных по рецепту.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    @staticmethod
    def get_ingredients(obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        return ShowIngredientsInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """
        Проверка на наличие рецепта в избранном.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(recipe=obj,
                                             user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверка на наличие рецепта в списке покупок.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=obj,
                                           user=request.user).exists()


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления Ингредиентов.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления рецептов.
    """
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    name = serializers.CharField(max_length=200)
    cooking_time = serializers.IntegerField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags',
                  'image', 'name', 'text',
                  'cooking_time', 'author')

    def validate_ingredients(self, data):
        """
        Проверка ингредиентов.
        """
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                'Необходимо выбрать ингредиенты!'
            )
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше нуля!'
                )
        ids = [item['id'] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise ValidationError(
                'Ингредиенты в рецепте должны быть уникальными!'
            )
        for _id in ids:
            if not Ingredient.objects.filter(id=_id).exists():
                raise ValidationError(
                    f'Ингредиент с id = {_id} не найден!'
                )
        return data

    @staticmethod
    def validate_cooking_time(value):
        if value <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше нуля!'
            )
        return value

    @staticmethod
    def add_ingredients(ingredients, recipe):
        for ingr in ingredients:
            ingr_id = ingr['id']
            amount = ingr['amount']
            if RecipeIngredients.objects.filter(
                    recipe=recipe, ingredient=ingr_id).exists():
                amount += F('amount')
            RecipeIngredients.objects.update_or_create(
                recipe=recipe, ingredient=ingr_id,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        recipe.image = image
        recipe.save()
        return recipe

    def update(self, recipe, validated_data):
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)
        recipe.image = validated_data.get(
            'image', recipe.image)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.add_ingredients(ingredients, recipe)
        if 'tags' in self.initial_data:
            tags = validated_data.pop('tags')
            recipe.tags.clear()
            recipe.tags.set(tags)
        recipe.save()
        return recipe

    def to_representation(self, recipe):
        data = ShowRecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}).data
        return data


class ShowFavoriteRecipeShopListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого отображения сведений о рецепте.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка избранного.
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if FavoriteRecipe.objects.filter(user=user,
                                         recipe__id=recipe_id).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowFavoriteRecipeShopListSerializer(
            instance.recipe,
            context=context
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if ShoppingList.objects.filter(user=user,
                                       recipe__id=recipe_id).exists():
            raise ValidationError(
                'Рецепт уже добавлен в корзину!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowFavoriteRecipeShopListSerializer(
            instance.recipe,
            context=context
        ).data
