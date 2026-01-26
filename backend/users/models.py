from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Используется e-mail в качестве уникального индентификатора вместо username.
    """
    email = models.EmailField(
        'email address',
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
    )
    image = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
        default=None
    )

    # Используем e-mail вместо username для авторизации
    USERNAME_FIELD = 'email'
    # Обязательные поля при создании пользователя через createsuperuser
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.email


class Follow(models.Model):
    """
    Модель подписки пользователя на автора.
    Пользователь подписывается на автора.
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
