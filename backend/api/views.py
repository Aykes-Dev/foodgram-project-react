from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from django_filters import rest_framework as filters

from api.paginators import PaginationForRecipe
from api.serializers import (
    FollowSerializator, IngredientSerializer, TagSerializer, UserSerializer,
    RecipeSerializer, FavoriteSerializer, CreateRecipeSerializer,
    RecipeForFollowwerSerializer)
from recipes.custom_filters import RecipeFilter
from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingList, CountIngredient)
from users.models import Follow, User

ERROR_MESSAGE_SUBSCRIBE = 'Нельзя подписаться на себя.'
ERROR_MESSAGE_NOT_SUBSCRIBE = 'Подписка не найдена.'
ALREADY_ADDED_TO_FAVORITES = 'Рецепт уже добавлен в избранное.'
ALREADY_ADDED_TO_SHOP_LIST = 'Рецепт уже добавлен в список покупок.'


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            FollowSerializator(
                self.paginate_queryset(
                    Follow.objects.filter(user=request.user)), many=True).data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True
    )
    def subscribe(self, request, id):
        following = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == 'POST':
            if user.id == following.id:
                return Response(
                    {'error': ERROR_MESSAGE_SUBSCRIBE}, status=400)
            return Response(
                FollowSerializator(
                    Follow.objects.create(
                        user=user, following=following),
                    context={'request': request}).data,
                status=201
            )
        follow = Follow.objects.filter(user=user, following=following)
        if follow.exists():
            follow.delete()
            return Response(status=204)
        return Response({'error': ERROR_MESSAGE_NOT_SUBSCRIBE}, status=400)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PaginationForRecipe

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def add_or_delete(self, model, message, request, pk, serializers):
        if request.method == 'DELETE':
            model.objects.get(
                user=request.user, repice=get_object_or_404(Recipe, id=pk)
                ).delete()
            return Response(status=204)
        recipe = get_object_or_404(Recipe, id=pk)
        _, create = model.objects.get_or_create(
            user=request.user, repice=recipe)
        if not create:
            return Response({'errors': message}, status=400)
        serializer = serializers(recipe)
        return Response(serializer.data, status=201)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        return self.add_or_delete(
            Favorite, ALREADY_ADDED_TO_FAVORITES, request, pk,
            FavoriteSerializer)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        return self.add_or_delete(
            ShoppingList, ALREADY_ADDED_TO_SHOP_LIST, request, pk,
            RecipeForFollowwerSerializer)

    """@action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        if request.method == 'DELETE':
            Favorite.objects.get(
                user=request.user, repice=get_object_or_404(Recipe, id=pk)
                ).delete()
            return Response(status=204)
        _, create = Favorite.objects.get_or_create(
            user=request.user, repice=get_object_or_404(Recipe, id=pk))
        if not create:
            return Response({'errors': ALREADY_ADDED_TO_FAVORITES}, status=400)
        serializer = FavoriteSerializer(get_object_or_404(Recipe, id=pk))
        return Response(serializer.data, status=201)"""

    """@action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        if request.method == 'DELETE':
            ShoppingList.objects.get(
                user=request.user, repice=get_object_or_404(Recipe, id=pk)
                ).delete()
            return Response(status=204)
        _, create = ShoppingList.objects.get_or_create(
            user=request.user, repice=get_object_or_404(Recipe, id=pk))
        if not create:
            return Response({'errors': ALREADY_ADDED_TO_SHOP_LIST}, status=400)
        serializer = RecipeForFollowwerSerializer(
            get_object_or_404(Recipe, id=pk))
        return Response(serializer.data, status=201)"""

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        ingredients = CountIngredient.objects.filter(
            recipe__shopping_list__user=request.user).values(
                'ingredients__name', 'ingredients__measurement_unit').annotate(
                    value=Sum('amount')).order_by('ingredients__name')
        response = HttpResponse(
            content_type='text/plain',
            charset='utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt')
        for ingredient in ingredients:
            print(ingredient)
            response.write(
                f"{ingredient['ingredients__name']}: "
                f"{ingredient['value']} "
                f"{ingredient['ingredients__measurement_unit']}.\n")
        return response
