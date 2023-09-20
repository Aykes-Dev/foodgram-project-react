from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (CountIngredient, Favorite, Follow, Ingredient,
                            Recipe, ShoppingList, Tag, User)


ERROR_MESSAGE_COOKING_TIME = 'Время приготовления не может быть меньше 1 мин.'


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
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True, max_length=256)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            return email
        raise serializers.ValidationError('Такой email уже сущевствует.')


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
        return RecipeForFollowwerSerializer(
            source.following.recipes.all(), many=True).data


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
        model = CountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class CreateIngredientCountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = CountIngredient
        fields = ('id', 'amount', )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientCountSerializer(
        many=True, read_only=True, source='countingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def check(self, model, recipe):
        user = self.context['request'].user
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
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = CreateIngredientCountSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'name', 'ingredients', 'cooking_time', 'text', 'image', 'tags')

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            return serializers.ValidationError(ERROR_MESSAGE_COOKING_TIME)
        return cooking_time

    def create_ingredient(self, recipe, ingredients):
        for ingredient in ingredients:
            CountIngredient.objects.create(
                recipe=recipe,
                ingredients=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount'])

    def pop_elements(self, data, pop_list):
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
        CountIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredient(recipe=instance, ingredients=ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
