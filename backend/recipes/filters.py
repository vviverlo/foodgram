from django.db.models import Case, IntegerField, Q, When
from django_filters import CharFilter
from django_filters.rest_framework import BooleanFilter, FilterSet

from .models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = CharFilter(method='filter_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_by_name(self, queryset, name, value):
        value = (value or '').strip()
        if not value:
            return queryset.order_by('name')
        return (
            queryset.filter(name__istartswith=value)
            .annotate(
                sort_order=Case(
                    When(name__iexact=value, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
            )
            .order_by('sort_order', 'name')
        )


class RecipeFilter(FilterSet):
    tags = CharFilter(method='filter_tags_by_slug')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags_by_slug(self, queryset, name, value):
        slugs = self.data.getlist('tags')
        if not slugs:
            return queryset
        q = Q()
        for slug in slugs:
            q |= Q(tags__slug=slug)
        return queryset.filter(q).distinct()

    def filter_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        return queryset.filter(recipes_favorite__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        return queryset.filter(recipes_shoppingcart__user=user)

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()
