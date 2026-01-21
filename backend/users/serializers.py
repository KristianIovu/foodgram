from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import ValidationError

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise ValidationError({"password2": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return super().create(validated_data)
