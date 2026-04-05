from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 0


class RecipesCountAdminMixin:
    """Аннотация количества связанных рецептов для списка в админке."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_recipes_count=Count('recipes', distinct=True))

    @admin.display(description='Рецептов', ordering='_recipes_count')
    def recipes_count(self, obj):
        return obj._recipes_count


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date', 'favorite_count')
    list_filter = ('tags',)
    search_fields = ('name', 'author__username', 'author__email')
    readonly_fields = ('favorite_count', 'short_code', 'pub_date')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_favorite_count=Count('recipes_favorite'))

    @admin.display(description='В избранном', ordering='_favorite_count')
    def favorite_count(self, obj):
        return obj._favorite_count


@admin.register(Tag)
class TagAdmin(RecipesCountAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
