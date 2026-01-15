from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Tag, Ingredient, Recipe

User = get_user_model()

class RecipesModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.tag = Tag.objects.create(
            name='Завтрак',
            slug='breakfast'
        )
        
        self.ingredient = Ingredient.objects.create(
            name='Мука',
            measurement_unit='г'
        )
        
    def test_tag_str(self):
        self.assertEqual(str(self.tag), 'Завтрак')
        
    def test_ingredient_str(self):
        self.assertEqual(str(self.ingredient), 'Мука, г')
        
    def test_tag_unique_slug(self):
        """Тест уникальности слага"""
        with self.assertRaises(Exception):
            Tag.objects.create(
                name='Другой завтрак',
                slug='breakfast'  # Должен быть уникальным
            )
            
    def test_ingredient_unique_constraint(self):
        """Тест уникальности комбинации имя+единица измерения"""
        # Первый создан в setUp
        # Второй с такими же данными должен вызвать ошибку
        with self.assertRaises(Exception):
            Ingredient.objects.create(
                name='Мука',
                measurement_unit='г'
            )
