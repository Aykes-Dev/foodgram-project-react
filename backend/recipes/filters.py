from django_filters import rest_framework as filters
from recipes.models import Ingredient

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='get_favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='shopping_cart_filter'
    )
    author = filters.CharFilter(field_name='author')

    def get_favorite(self, *_):
        if self.request.user.is_anonymous:
            return Recipe.objects.all()
        return Recipe.objects.filter(favorites__user=self.request.user)

    def shopping_cart_filter(self, *_):
        if self.request.user.is_anonymous:
            return Recipe.objects.all()
        return Recipe.objects.filter(shopping_list__user=self.request.user)


class TagFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='slug')


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith', )

    class Meta:
        model = Ingredient
        fields = ('name',)
