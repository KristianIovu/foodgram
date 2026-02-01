from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import Follow

User = get_user_model()


@admin.register(User)
class UserModelAdmin(UserAdmin):
    """Админ интерфейс для модели пользователя."""
    list_display = ('id', 'email',
                    'username',
                    'first_name',
                    'last_name',
                    'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active',
                                    'is_staff',
                                    'is_superuser',
                                    'groups',
                                    'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',
                       'username',
                       'first_name',
                       'last_name',
                       'password1',
                       'password2'),
        }),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ интерфейс для модели подписок."""
    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__email', 'author__email')
