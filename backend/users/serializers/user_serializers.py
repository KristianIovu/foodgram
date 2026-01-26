from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'required': True,
                'validators': [UniqueValidator(
                    queryset=User.objects.all(),
                    message='Пользователь с таким email уже существует'
                )]
            }
        }


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    # 1. Делаем поле НЕобязательным (required=False)
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        # 2. Проверяем совпадение, только если пароль пришел (для тестов/curl)
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password2 and password != password2:
            raise serializers.ValidationError(
                {'password2': 'Пароли не совпадают'}
            )
        return attrs

    def create(self, validated_data):
        # 3. Безопасно удаляем password2, если оно есть
        validated_data.pop('password2', None)
        # create_user захеширует пароль корректно
        user = User.objects.create_user(**validated_data)
        return user


class UserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль неверен')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
