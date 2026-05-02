from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password')
        extra_fields = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if confirm_password != password:
            raise ValidationError({'confirm_password': 'Пароли не совпадают'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        return {
            "user_id": instance.id,
            "email": instance.email,
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError("Пользователь не найден")
        if not user.is_active:
            raise serializers.ValidationError('Пользователь неактивен')

        if not user.check_password(data['password']):
            raise serializers.ValidationError("Неверный пароль")

        data['user'] = user
        return data

    def to_representation(self, instance):
        return {
            "user_id": instance.id,
            "email": instance.email,
            "activation_key": instance.activation_key,
            "activation_key_expires": instance.activation_key_expires,
        }


class ProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'activation_key', 'activation_key_expires')


class PasswordResetSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class ActivationKeySerializer(serializers.Serializer):
    activation_key = serializers.CharField()

    def validate(self, data):
        key = data.get('activation_key')
        try:
            user = User.objects.get(activation_key=key)
        except User.DoesNotExist:
            raise ValidationError('Неверный ключ активации')

        if not user.is_activation_key_valid(key):
            raise ValidationError('Ключ активации истёк')

        data['user'] = user
        return data

