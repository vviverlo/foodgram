from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from .serializers import SetAvatarSerializer, SubscriptionUserSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    def get_permissions(self):
        if getattr(self, 'action', None) == 'me':
            self.permission_classes = (IsAuthenticated,)
            return super().get_permissions()
        return super().get_permissions()

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        authors = (
            User.objects.filter(subscribers__user=request.user)
            .distinct()
            .order_by('username')
        )
        page = self.paginate_queryset(authors)
        context = self.get_serializer_context()
        context['recipes_limit'] = request.query_params.get('recipes_limit')
        context['force_subscribed'] = True
        serializer = SubscriptionUserSerializer(
            page,
            many=True,
            context=context,
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
    )
    def subscribe(self, request, **kwargs):
        author = self.get_object()
        context = self.get_serializer_context()
        context['recipes_limit'] = request.query_params.get('recipes_limit')
        context['force_subscribed'] = True
        if request.method == 'POST':
            if author.pk == request.user.pk:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            _, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author,
            )
            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            data = SubscriptionUserSerializer(
                author,
                context=context,
            ).data
            return Response(data, status=status.HTTP_201_CREATED)
        deleted, _ = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(
                request.user,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'avatar': request.user.avatar.url})
        if request.user.avatar:
            request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)
