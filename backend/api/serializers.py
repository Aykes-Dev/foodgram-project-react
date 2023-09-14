from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, CountIngredient, Favorite
from users.models import User, Follow


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
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class FollowSerializator(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, source):
        return Follow.objects.filter(
            user=source.user, following=source.following).exists()

    def get_recipes(self, source):
        recipes = Recipe.objects.filter(author=source.following)
        serializer = RecipeForFollowwerSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, source):
        return Recipe.objects.filter(author=source.following).count()


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

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if not user.is_authenticated:
            print("AnonymousUser")
            return False
        return Favorite.objects.filter(user=user, repice=recipe).exists()

    def get_is_in_shopping_cart(self, source):
        return False

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


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
