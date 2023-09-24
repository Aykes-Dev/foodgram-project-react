from collections import Counter
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Composition, Favorite, Follow, Ingredient,
                            Recipe, ShoppingList, Tag, User)

ERROR_MESSAGE_IMAGE = 'Изображение обязательное поле'
ERROR_MESSAGE_TAGS = 'Нельзя указать два одинаковых тега: {}'
RROR_MESSAGE_INGRESIENTS = 'Нельзя указать два одинаковых ингредиента: {}'
DOES_NOT_EXISTS_INGREDIENT = 'Ингредиент не найден'
NOT_FOUND_MESSAGE = 'Отсутствует: {}'
LIST_EMPTY = 'Список {} не может быть пустым.'


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Follow.objects.filter(user=user, following=author).exists()


class CreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')


class FollowSerializator(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='following.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, source):
        return Follow.objects.filter(
            user=source.user, following=source.following).exists()

    def get_recipes(self, source):
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=source.following)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeForFollowwerSerializer(recipes, many=True).data


class RecipeForFollowwerSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientCountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = Composition
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class CreateIngredientCountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Composition
        fields = ('id', 'amount', )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientCountSerializer(
        many=True, read_only=True, source='compositions')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def check(self, model, recipe):
        user = self.context.get('request').user

        if not user.is_authenticated:
            return False
        return model.objects.filter(user=user, repice=recipe).exists()

    def get_is_favorited(self, recipe):
        return self.check(model=Favorite, recipe=recipe)

    def get_is_in_shopping_cart(self, recipe):
        return self.check(model=ShoppingList, recipe=recipe)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = CreateIngredientCountSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'name', 'ingredients', 'cooking_time', 'text', 'image', 'tags')

    def validate_image(self, image):
        if image == '' or image is None:
            return serializers.ValidationError(ERROR_MESSAGE_IMAGE)
        return image

    def validate_tags(self, tags):
        if tags == []:
            raise serializers.ValidationError(LIST_EMPTY.format('тегов'))
        if (repeat := ' '.join(
                tag.name for tag, count in Counter(tags).items() if count > 1
        )):
            raise serializers.ValidationError(
                ERROR_MESSAGE_TAGS.format(repeat))
        return tags

    def validate_ingredients(self, ingredients):
        if ingredients == []:
            raise serializers.ValidationError(
                LIST_EMPTY.format('ингредиентов'))
        items = []
        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(DOES_NOT_EXISTS_INGREDIENT)
            if ingredient['id'] in items:
                raise serializers.ValidationError(
                    RROR_MESSAGE_INGRESIENTS.format(
                        Ingredient.objects.get(id=ingredient['id'])))
            items.append(ingredient['id'])
        return ingredients

    @staticmethod
    def create_ingredient(recipe, ingredients):
        Composition.objects.bulk_create(
            Composition(
                recipe=recipe,
                ingredients=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']) for ingredient in ingredients)

    @staticmethod
    def pop_elements(data, pop_list):
        if (not_exists := [value for value in pop_list if value not in data]):
            raise serializers.ValidationError(
                NOT_FOUND_MESSAGE.format(not_exists))
        return *[data.pop(value) for value in pop_list], data

    def create(self, validated_data):
        tags, ingredients, validated_data = self.pop_elements(
            validated_data, ['tags', 'ingredients'])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredient(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags, ingredients, validated_data = self.pop_elements(
            validated_data, ['tags', 'ingredients'])
        instance.tags.set(tags)
        Composition.objects.filter(recipe=instance).delete()
        self.create_ingredient(recipe=instance, ingredients=ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
