from colorfield.fields import ColorField
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from users.models import User

MAX_LENGTH = 200


class Tag(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH, unique=True)
    color = ColorField(default='#FF0000', max_length=7)
    slug = models.SlugField('Слаг', max_length=MAX_LENGTH, unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name

    @admin.display(description='Цвет')
    def colored_name(self):
        return format_html(
            '<div style="background: {}; width: 20px; height: 20px;'
            ' border: 1px solid black;"> </div>',
            self.color
        )


class Ingredient(models.Model):
    CHOICES = (
        ('кг', 'кг'),
        ('г', 'г'),
    )
    name = models.CharField('Название', max_length=MAX_LENGTH, )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_LENGTH, choices=CHOICES)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class CountIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe', verbose_name='Рецепт', on_delete=models.CASCADE)
    ingredients = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        ordering = ('recipe', )
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        default_related_name = 'countingredient'

    def __str__(self) -> str:
        return f'{self.recipe} : {self.ingredients} - {self.amount}'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='Тег')
    author = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, verbose_name='Автор')
    ingredients = models.ManyToManyField(
        CountIngredient, verbose_name='Ингредиенты')
    name = models.CharField('Название', max_length=MAX_LENGTH)
    image = models.ImageField('Изображение', upload_to='recipe/')
    text = models.TextField('Описание')
    cooking_time = models.IntegerField('Время приготовления')

    class Meta:
        ordering = ('name', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self) -> str:
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    repice = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        ordering = ('user', )
        default_related_name = 'favorite'

    def __str__(self) -> str:
        return self.user.get_username() + ' ' + self.repice.name
