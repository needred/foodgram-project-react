from django.db.models import Sum

from recipes.models import Recipe


def get_list_ingredients(user):
    """
    Cуммирование позиций из разных рецептов.
    """

    ingredients = Recipe.objects.filter(
        shopping_recipe__user=user
    ).values('ingredients__name',
             'ingredients__measurement_unit').annotate(
        amount=Sum('recipe_ingredient__amount')).order_by().values_list(
        'ingredients__name', 'amount', 'ingredients__measurement_unit')
    return ingredients
