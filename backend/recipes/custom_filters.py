from django_filters import rest_framework as filters
from recipes.models import Ingredient

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='get_favorite')

    def get_favorite(self, *_):
        return Recipe.objects.filter(favorites__user=self.request.user)


class TagFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='slug')


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith', )

    class Meta:
        model = Ingredient
        fields = ('name',)
