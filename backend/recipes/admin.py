from django.contrib import admin
from django.contrib.auth.admin import Group
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingList,
                            Tag, User, Сomposition)

admin.site.unregister(Group)
LENGT_INGREDIENTS = 50
IMAGE_STATUS = '<img src="/static/admin/img/icon-{}.svg">'
IMAGE_STATUS = '<img src="{}" width="75px" heigth="75px">'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'colored_name', 'slug')
    list_filter = ('name', )
    search_fields = ('name', )

    @admin.display(description='Пример цвета')
    def colored_name(self, tag):
        return format_html(
            '<div style="background: {}; width: 20px; height: 20px"></div>',
            tag.color
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )
    search_fields = ('name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'count', 'author', 'image_admin', 'tags_admin',
        'ingredients_admin')
    list_filter = ('tags', )
    search_fields = ('author__username', 'name', 'tags__name')

    @admin.display(description='В избраном')
    def count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    def tags_admin(self, recipe):
        return format_html(
            ''.join('<div>- {}</div>'.format(
                item.name) for item in recipe.tags.all()))

    @admin.display(description='Ингредиенты')
    def ingredients_admin(self, recipe):
        return format_html(
            ''.join('<div>- {}</div>'.format(
                item.ingredients.name) for item in recipe.composition.all()
            ))

    @admin.display(description='Ингредиенты')
    def image_admin(self, recipe):
        a = recipe.image.url
        return mark_safe(IMAGE_STATUS.format(a))


@admin.register(Сomposition)
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
        'username', 'email', 'full_name', 'count_recipe', 'subscribers',
        'subscriptions', 'is_staff')
    search_fields = ('username', 'email')

    @admin.display(description='Фамилия Имя')
    def full_name(self, user):
        return f'{user.last_name} {user.first_name}'

    @staticmethod
    def get_status_image(value):
        return mark_safe(IMAGE_STATUS.format('yes' if value > 0 else 'no'))

    @admin.display(description='Подписчики')
    def subscribers(self, user):
        return self.get_status_image(user.following.count())

    @admin.display(description='Подписки')
    def subscriptions(self, user):
        return self.get_status_image(user.follower.count())

    @admin.display(description='Число рецептов')
    def count_recipe(self, user):
        return user.recipes.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follow', )
    search_fields = ('user__username', 'following__username')

    @admin.display(description='Подписки')
    def follow(self, follow, ):
        return f'{follow.user} подписан на {follow.following}'
