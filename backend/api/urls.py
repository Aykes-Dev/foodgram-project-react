
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = 'api'

router_version_1 = DefaultRouter()
router_version_1.register('users', UserViewSet, 'users')
router_version_1.register('tags', TagViewSet, 'tags')
router_version_1.register('ingredients', IngredientViewSet, 'ingredients')
router_version_1.register('recipes', RecipeViewSet, 'recipes')

urlpatterns = [
    path('', include(router_version_1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
