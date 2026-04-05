from django.contrib.auth import get_user_model
from recipes.fields import Base64ImageField
from rest_framework import serializers

from .models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        if self.context.get('force_subscribed'):
            return True
        request = self.context.get('request')
        return (
            request is not None
            and request.user.is_authenticated
            and obj.pk != request.user.pk
            and Subscription.objects.filter(
                user=request.user,
                author=obj,
            ).exists()
        )

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else None


class SubscriptionUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        from recipes.serializers import RecipeMinifiedSerializer

        limit = self.context.get('recipes_limit')
        qs = obj.recipes.order_by('-pub_date')
        if limit is not None:
            try:
                lim = int(limit)
                if lim > 0:
                    qs = qs[:lim]
            except (TypeError, ValueError):
                pass
        return RecipeMinifiedSerializer(
            qs,
            many=True,
            context=self.context,
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)
