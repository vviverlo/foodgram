from collections import defaultdict

from django.db.models import Case, IntegerField, When
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, RecipeMinifiedSerializer,
                          RecipeUpdateSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            name = name.strip()
            queryset = queryset.filter(name__istartswith=name)
            queryset = queryset.annotate(
                sort_order=Case(
                    When(name__iexact=name, then=0),
                    default=1,
                    output_field=IntegerField(),
                )
            ).order_by('sort_order', 'name')
        else:
            queryset = queryset.order_by('name')
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags',
        'recipe_ingredients__ingredient',
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        if self.action in ('partial_update', 'update'):
            return RecipeUpdateSerializer
        return RecipeListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        if tags:
            qs = qs.filter(tags__slug__in=tags).distinct()
        if self.request.query_params.get('is_favorited') == '1':
            if self.request.user.is_authenticated:
                qs = qs.filter(favorites__user=self.request.user)
            else:
                qs = qs.none()
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            if self.request.user.is_authenticated:
                qs = qs.filter(shopping_cart__user=self.request.user)
            else:
                qs = qs.none()
        return qs.distinct().order_by('-pub_date')

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            _obj, created = Favorite.objects.get_or_create(
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
        deleted, _ = Favorite.objects.filter(
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
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            _obj, created = ShoppingCart.objects.get_or_create(
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
        deleted, _ = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        recipes = Recipe.objects.filter(
            shopping_cart__user=request.user,
        ).prefetch_related(
            'recipe_ingredients__ingredient',
        )
        totals = defaultdict(int)
        for recipe in recipes:
            for ri in recipe.recipe_ingredients.all():
                totals[ri.ingredient_id] += ri.amount
        lines = []
        for ing in Ingredient.objects.filter(
            pk__in=totals.keys(),
        ).order_by('name'):
            amount = totals[ing.id]
            lines.append(f'{ing.name} ({ing.measurement_unit}) — {amount}')
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
