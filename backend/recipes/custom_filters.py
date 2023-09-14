from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='get_favorite')

    def get_favorite(self, *_):
        return Recipe.objects.filter(favorite__user=self.request.user)
