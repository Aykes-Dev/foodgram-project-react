from django.contrib import admin

from recipes.models import Tag, Ingredient, Recipe, CountIngredient, Favorite


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colored_name', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe)
admin.site.register(CountIngredient)
admin.site.register(Favorite)
