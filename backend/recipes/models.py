from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from recipes.validators import validate_username


MAX_LENGTH = 200
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_NAME = 150

FOLLOW_STR = '{0} подписан на {1}'
SUBSCRIBE_ERROR = 'Нельзя подписаться на себя.'


class User(AbstractUser):
    email = models.EmailField(
        'Адрес электронной почты', max_length=MAX_LENGTH_EMAIL, unique=True)
    username = models.CharField(
        'Имя пользователя', max_length=MAX_LENGTH_NAME, unique=True,
        validators=(validate_username, ))
    first_name = models.CharField(
        'Имя', max_length=MAX_LENGTH_NAME, unique=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_LENGTH_NAME, unique=True,
    )
    password = models.CharField(
        'Пароль', max_length=MAX_LENGTH_NAME, unique=True,
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'users'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Автор')

    class Meta:
        ordering = ('user', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='follow_user_author_constraint'),
        )

    def __str__(self) -> str:
        return FOLLOW_STR.format(
            self.user.get_username(), self.following.get_username())

    def clean(self):
        if self.user == self.following:
            raise ValidationError(SUBSCRIBE_ERROR)


class Tag(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH, unique=True)
    color = models.CharField(
        'Цвет', default='#FF0000', max_length=7, unique=True)
    slug = models.SlugField('Слаг', max_length=MAX_LENGTH, unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH, )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_LENGTH)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        default_related_name = 'ingredients'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique ingredient')
        ]

    def __str__(self) -> str:
        return self.name


class CountIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe', verbose_name='Рецепт', on_delete=models.CASCADE)
    ingredients = models.ForeignKey(
        Ingredient, verbose_name='Продукты', on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        ordering = ('recipe', )
        verbose_name = 'Количество продуктов'
        verbose_name_plural = 'Количество продуктов'
        default_related_name = 'countingredient'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredients'],
                                    name='unique coun tingredient')
        ]

    def __str__(self) -> str:
        return f'{self.recipe} : {self.ingredients} - {self.amount}'

    @staticmethod
    def count_ingredient(self, user):
        return self.objects.filter(
            recipe__shopping_list__user=user).values(
                'ingredients__name', 'ingredients__measurement_unit').annotate(
                    value=Sum('amount')).order_by('ingredients__name')


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='Тег')
    author = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, verbose_name='Автор')
    ingredients = models.ManyToManyField(
        CountIngredient, verbose_name='Продукты')
    name = models.CharField('Название', max_length=MAX_LENGTH, unique=True)
    image = models.ImageField('Изображение', upload_to='recipe/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления')

    class Meta:
        ordering = ('name', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self) -> str:
        return self.name


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    repice = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        abstract = True
        ordering = ('user', )

    def __str__(self) -> str:
        return f'{self.user.get_username()} добавил {self.repice.name}'


class Favorite(UserRecipe):

    class Meta(UserRecipe.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingList(UserRecipe):
    class Meta(UserRecipe.Meta):
        default_related_name = 'shopping_list'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
