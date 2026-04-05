from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import OwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, RecipeMinifiedSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, OwnerOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        qs = Recipe.objects.select_related('author').prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
        )
        return qs.with_user_recipe_flags(self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeListSerializer

    def _user_recipe_relation_response(self, request, recipe, relation_model):
        if request.method == 'POST':
            _, created = relation_model.objects.get_or_create(
                user=request.user,
                recipe=recipe,
            )
            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            data = RecipeMinifiedSerializer(
                recipe,
                context={'request': request},
            ).data
            return Response(data, status=status.HTTP_201_CREATED)
        deleted, _ = relation_model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        return self._user_recipe_relation_response(request, recipe, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        return self._user_recipe_relation_response(
            request,
            recipe,
            ShoppingCart,
        )

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        path = f'/s/{recipe.short_code}/'
        url = request.build_absolute_uri(path)
        return Response({'short-link': url})

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        rows = (
            RecipeIngredient.objects.filter(
                recipe__recipes_shoppingcart__user=request.user,
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )
        lines = [
            (
                f"{row['ingredient__name']} "
                f"({row['ingredient__measurement_unit']}) — {row['total']}"
            )
            for row in rows
        ]
        content = '\n'.join(lines)
        if content:
            content += '\n'
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response


def recipe_short_link_redirect(request, short_code):
    """Редирект с короткой ссылки на страницу рецепта во фронтенде."""
    try:
        recipe = Recipe.objects.get(short_code=short_code)
    except Recipe.DoesNotExist:
        return redirect('/not-found')
    return redirect(f'/recipes/{recipe.pk}/')
