from django.contrib import admin
from django.contrib.auth import get_user_model
from users.models import Subscription

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Админка для пользователей.
    """
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'date_joined', 'posts_count', 'subscriptions_count'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('date_joined',)
    ordering = ('-date_joined',)

    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Публикаций'

    def subscriptions_count(self, obj):
        return obj.follower.count()
    subscriptions_count.short_description = 'Подписок'
