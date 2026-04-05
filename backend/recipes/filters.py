import django_filters as df

from .models import Recipe


class RecipeFilter(df.FilterSet):
    tags = df.CharFilter(method='filter_tags')
    author = df.NumberFilter(field_name='author__id')
    is_favorited = df.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = df.NumberFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset
