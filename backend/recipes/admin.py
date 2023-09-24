from django.contrib import admin
from django.contrib.auth.admin import Group
from django.db.models import Max, Min
from django.utils.html import format_html

from recipes.models import (
    Composition, Favorite, Follow, Ingredient, Recipe, ShoppingList, Tag, User)

admin.site.unregister(Group)
LENGT_INGREDIENTS = 50
IMAGE_RECIPE = '<img src="{}" width="75px" heigth="75px">'
COLOR_VIEW = '<span  style="background: {};">&nbsp&nbsp&nbsp&nbsp&nbsp</span>'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'get_color_html', 'slug')
    list_filter = ('name', )
    search_fields = ('name', )

    @admin.display(description='Пример цвета')
    def get_color_html(self, tag):
        return format_html(COLOR_VIEW, tag.color)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )
    search_fields = ('name', 'measurement_unit')


class IngredientInline(admin.TabularInline):
    model = Composition
    extra = 3
    min_num = 1


class CookingTimeFilter(admin.SimpleListFilter):
    title = ('Скорость приготовления')
    parameter_name = 'cooking_time'

    def get_value(self, queryset):
        min_value, max_value = queryset.aggregate(
            Min("cooking_time"),
            Max("cooking_time")).values()
        porog = int((max_value - min_value) * 0.33)
        return min_value, porog, porog * 2, max_value

    def lookups(self, request, model_admin):
        qu = model_admin.get_queryset(request)
        min_value, first_porog, secound_porog, max_value = self.get_value(qu)
        return (
            ('fast', ('Быстрое {}-{} минут'.format(
                min_value, first_porog))),
            ('middle', ('Среднее {}-{} минут'.format(
                first_porog, secound_porog))),
            ('slow', ('Медленное {}-{} минут'.format(
                secound_porog, max_value))),
        )

    def queryset(self, _, queryset):
        min_value, first_porog, secound_porog, max_value = self.get_value(
            queryset)
        if self.value() == 'fast':
            return queryset.filter(
                cooking_time__range=[min_value, first_porog])
        if self.value() == 'middle':
            return queryset.filter(
                cooking_time__range=[first_porog + 1, secound_porog])
        if self.value() == 'slow':
            return queryset.filter(
                cooking_time__range=[secound_porog + 1, max_value])
        return queryset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'get_count_in_favorite', 'author', 'get_image', 'get_tags',
        'get_ingredients')
    list_filter = ('tags', CookingTimeFilter,)
    search_fields = ('author__username', 'name', 'tags__name')
    inlines = (IngredientInline,)

    @admin.display(description='В избраном')
    def get_count_in_favorite(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return format_html(
            '<br>'.join(item.name for item in recipe.tags.all()))

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return format_html(
            '<br>'.join(
                f'{item.ingredients.name} '
                f'{item.amount} '
                f'{item.ingredients.measurement_unit}'
                for item in recipe.compositions.all()
            ))

    @admin.display(description='Изображение')
    def get_image(self, recipe):
        return format_html(IMAGE_RECIPE.format(recipe.image.url))


@admin.register(Composition)
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
    list_display = (
        'username', 'email', 'get_full_name', 'get_count_recipe',
        'get_subscribers', 'get_subscriptions', 'is_staff')
    search_fields = ('username', 'email')

    @admin.display(description='Фамилия Имя')
    def get_full_name(self, user):
        return f'{user.last_name} {user.first_name}'

    @admin.display(description='Подписчики')
    def get_subscribers(self, user):
        return user.following.count()

    @admin.display(description='Подписки')
    def get_subscriptions(self, user):
        return user.follower.count()

    @admin.display(description='Число рецептов')
    def get_count_recipe(self, user):
        return user.recipes.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('get_follow_title', )
    search_fields = ('user__username', 'following__username')

    @admin.display(description='Подписки')
    def get_follow_title(self, follow, ):
        return f'{follow.user.username} подписан на {follow.following}'
