from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

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
        if not request or not request.user.is_authenticated:
            return False
        if obj.pk == request.user.pk:
            return False
        from recipes.models import Subscription

        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        url = obj.avatar.url
        if request:
            return request.build_absolute_uri(url)
        return url


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        user = User(
            email=attrs.get('email'),
            username=attrs.get('username'),
            first_name=attrs.get('first_name'),
            last_name=attrs.get('last_name'),
        )
        validate_password(attrs['password'], user)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(
            email=validated_data['email'],
            password=password,
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )


class UserWithRecipesSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        if self.context.get('force_subscribed'):
            return True
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if obj.pk == request.user.pk:
            return False
        from recipes.models import Subscription

        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        url = obj.avatar.url
        if request:
            return request.build_absolute_uri(url)
        return url

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


class SetAvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField()

    def validate_avatar(self, value):
        if not value.startswith('data:image'):
            raise serializers.ValidationError(
                'Ожидается изображение в Base64.',
            )
        return value
