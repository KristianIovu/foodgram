from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    password2 = serializers.CharField(write_only=True, required=False)
    
    class Meta(BaseUserCreateSerializer.Meta):
        fields = BaseUserCreateSerializer.Meta.fields
    
    def validate(self, attrs):
        # Не проверяем password2
        if 'password2' in attrs:
            attrs.pop('password2')
        return attrs
