from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy


class User(AbstractUser):
    """Кастомная модель пользователя с email в качестве логина."""
    email = models.EmailField(unique=True, verbose_name='Email')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Модель подписки одного пользователя на другого."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author_subscription'
            ),
        ]

    def clean(self):
        """Проверка: нельзя подписаться на самого себя."""
        if self.user == self.author:
            raise ValidationError(_('Нельзя подписаться на самого себя.'))

    def save(self, *args, **kwargs):
        """Валидация при сохранении через админку и код."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return format_lazy('{0} → {1}', self.user, self.author)