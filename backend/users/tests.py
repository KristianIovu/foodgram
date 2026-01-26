from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UsersModelsTestCase(TestCase):
    """Тесты для модели пользователя."""
    def test_create_user(self):
        """Тест создания обычного пользователя."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Тест создания админа."""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_user_str(self):
        """Тест строкового представления пользователя (возвразает e-mail.)"""
        user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(str(user), 'john@example.com')
