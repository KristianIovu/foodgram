from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name")

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)