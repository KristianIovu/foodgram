from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F
import inspect

from .constants import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH


def build_follow_constraints():
    """
    Создаёт ограничения для модели Follow
    с учётом версии Django (check / condition).
    """
    expr = ~Q(user=F('author'))
    params = inspect.signature(models.CheckConstraint).parameters

    if 'check' in params:
        check_constraint = models.CheckConstraint(
            check=expr,
            name='prevent_self_follow'
        )
    else:
        check_constraint = models.CheckConstraint(
            condition=expr,
            name='prevent_self_follow'
        )

    return [
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follow'
        ),
        check_constraint,
    ]


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Используется email вместо username.
    """
    email = models.EmailField(
        'email address',
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    first_name = models.CharField(
        'first name',
        max_length=NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'last name',
        max_length=NAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
        default=None
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['email']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Follow(models.Model):
    """
    Подписка пользователя на автора.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = build_follow_constraints()

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
