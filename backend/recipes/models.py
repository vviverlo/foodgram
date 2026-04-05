import secrets
import string

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (INGREDIENT_NAME_MAX_LENGTH, INGREDIENT_UNIT_MAX_LENGTH,
                        RECIPE_NAME_MAX_LENGTH,
                        RECIPE_SHORT_CODE_GENERATED_LENGTH,
                        RECIPE_SHORT_CODE_MAX_LENGTH, TAG_NAME_MAX_LENGTH,
                        TAG_SLUG_MAX_LENGTH)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='recipes_ingredient_name_unit_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_NAME_MAX_LENGTH,
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин.)',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    short_code = models.CharField(
        'Короткий код ссылки',
        max_length=RECIPE_SHORT_CODE_MAX_LENGTH,
        unique=True,
        editable=False,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def _generate_unique_short_code(self):
        alphabet = string.ascii_letters + string.digits
        while True:
            code = ''.join(
                secrets.choice(alphabet)
                for _ in range(RECIPE_SHORT_CODE_GENERATED_LENGTH)
            )
            qs = Recipe.objects.filter(short_code=code)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if not qs.exists():
                return code

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self._generate_unique_short_code()
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='%(app_label)s_%(class)s_recipe_ingredient_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} — {self.amount}'


class UserRecipeRelation(models.Model):
    """Общая связь пользователь — рецепт (избранное, список покупок)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_user_recipe_uniq',
            ),
        ]


class Favorite(UserRecipeRelation):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeRelation):
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
