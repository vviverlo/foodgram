from django.contrib.auth.models import AbstractUser
from django.db import models

USER_NAME_MAX_LENGTH = 150


class User(AbstractUser):
    first_name = models.CharField('Имя', max_length=USER_NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=USER_NAME_MAX_LENGTH)
    email = models.EmailField('Адрес электронной почты', unique=True)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        db_table = 'recipes_subscription'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='%(app_label)s_%(class)s_user_author_uniq',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='%(app_label)s_%(class)s_not_self',
            ),
        ]
