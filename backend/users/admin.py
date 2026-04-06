from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from recipes.admin import RecipesCountAdminMixin

from .models import Subscription

User = get_user_model()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


@admin.register(User)
class UserAdmin(RecipesCountAdminMixin, BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'recipes_count',
        'is_staff',
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Персональные данные',
            {
                'fields': (
                    'username',
                    'first_name',
                    'last_name',
                    'avatar',
                ),
            },
        ),
        (
            'Права',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ),
            },
        ),
    )
