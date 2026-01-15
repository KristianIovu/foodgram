from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class SimpleTest(TestCase):
    def test_sample(self):
        self.assertEqual(1 + 1, 2)
