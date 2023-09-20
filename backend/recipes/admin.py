from django.contrib import admin
from django.contrib.auth.admin import Group
from django.utils.html import format_html

from recipes.models import (
    Tag, Ingredient, Recipe, CountIngredient, Favorite, ShoppingList, User)


admin.site.unregister(Group)
LENGT_INGREDIENTS = 50


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colored_name', 'slug')
    list_filter = ('name', )
    search_fields = ('name', )

    @admin.display
    def colored_name(self, tag):
        return format_html(
            '<span style="color: {};">{}</span>',
            tag.color,
            tag.color,
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )
    search_fields = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'count', 'author', 'tags_admin', 'ingredients_admin')
    list_filter = ('tags', )
    search_fields = ('author__username', 'name', 'tags__name')

    @admin.display(description='В избраном')
    def count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    def tags_admin(self, recipe):
        return ', '.join([item.name for item in recipe.tags.all()])

    @admin.display(description='Ингредиентыы')
    def ingredients_admin(self, recipe):
        if len(result := ', '.join(
            [item.ingredients.name for item in recipe.countingredient.all()])
        ) > LENGT_INGREDIENTS:
            result = result[:LENGT_INGREDIENTS] + '...'
        return result


@admin.register(CountIngredient)
class CountIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    search_fields = ('recipe__name', )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ('recipe__name', 'user_username')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    search_fields = ('recipe__name', 'user_username')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', )
    search_fields = ('username', 'email')
