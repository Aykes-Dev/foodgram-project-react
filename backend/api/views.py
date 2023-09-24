from datetime import date

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from djoser.views import UserViewSet
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginators import LimitPagination
from api.serializers import (CreateRecipeSerializer, FavoriteSerializer,
                             FollowSerializator, IngredientSerializer,
                             RecipeForFollowwerSerializer, RecipeSerializer,
                             TagSerializer, UserSerializer)
from recipes.filters import IngredientFilter, RecipeFilter, TagFilter
from recipes.models import (Composition, Favorite, Follow, Ingredient,
                            Recipe, ShoppingList, Tag, User)


ERROR_MESSAGE_NOT_SUBSCRIBE = 'Подписка не найдена.'
ALREADY_ADDED_TO_FAVORITES = 'Рецепт уже добавлен в избранное.'
ALREADY_ADDED_TO_SHOP_LIST = 'Рецепт уже добавлен в список покупок.'
TEMPLATE_SHOP_LIST = '{0}: {1} {2} '


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagination

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            FollowSerializator(
                self.paginate_queryset(
                    request.user.follower.all()),
                context={
                    'request': request,
                }, many=True
            ).data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True
    )
    def subscribe(self, request, id):
        following = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == 'POST':
            return Response(
                FollowSerializator(
                    Follow.objects.create(
                        user=user, following=following),
                    context={'request': request}
                ).data, status=201
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
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TagFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def add_or_delete(self, model, message, request, pk, serializers):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'DELETE':
            model.objects.get(
                user=request.user, repice=recipe).delete()
            return Response(status=204)
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

    def create_shopping_list(self, ingredients):
        return ''.join(
            TEMPLATE_SHOP_LIST.format(
                ingredient["ingredients__name"],
                ingredient["ingredients__measurement_unit"],
                ingredient["value"]) for ingredient in ingredients)

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        return FileResponse(
            self.create_shopping_list(
                Composition.get_count_ingredients(request.user)
            ), content_type='text/plain',
            filename=f'{date.today()}shopping_list.txt')
