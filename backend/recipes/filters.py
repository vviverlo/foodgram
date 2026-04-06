from django.db.models import Case, IntegerField, When
from django_filters import CharFilter
from django_filters.rest_framework import (
    BooleanFilter, FilterSet, ModelMultipleChoiceFilter,
)

from .models import Ingredient, Recipe, Tag


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
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = BooleanFilter(field_name='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
