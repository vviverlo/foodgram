from django.db import transaction
from rest_framework import serializers

from users.serializers import UserSerializer

from .fields import Base64ImageField
from .models import Ingredient, Recipe, RecipeIngredient, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.BooleanField(
        read_only=True,
        default=False,
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False,
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно прикрепить изображение.',
            )
        return value

    def validate(self, attrs):
        if self.instance is None and 'image' not in (self.initial_data or {}):
            raise serializers.ValidationError(
                {'image': 'Нужно прикрепить изображение.'},
            )

        ingredients = attrs.get('ingredients')
        tags = attrs.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Обязательное поле.'},
            )
        ingredient_keys = [row['ingredient'].pk for row in ingredients]
        if len(ingredient_keys) != len(set(ingredient_keys)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться.'},
            )
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужен хотя бы один тег.'},
            )
        tag_ids = [tag.pk for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться.'},
            )

        return attrs

    @staticmethod
    def _set_recipe_ingredients(recipe, ingredients_rows):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=row['ingredient'],
                    amount=row['amount'],
                )
                for row in ingredients_rows
            ],
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_rows = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context['request']
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self._set_recipe_ingredients(recipe, ingredients_rows)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_rows = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._set_recipe_ingredients(instance, ingredients_rows)
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url if obj.image else None
