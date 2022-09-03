from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .validators import phone_validator
from django_redis import get_redis_connection


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号", validators=[phone_validator])
    code = serializers.CharField(label="短信验证码")

    def validate_code(self, value):
        if (len(value) != 4):
            raise ValidationError("短信格式错误")
        if not value.isdecimal():
            raise ValidationError("短信格式错误")
        phone = self.initial_data.get('phone')
        conn = get_redis_connection()
        code = conn.get(phone)
        if not code:
            raise ValidationError("验证码过期")
        if value != code.decode('utf-8'):
            raise ValidationError("验证码错误")
        return value


class MessageSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])

    # def validate_phone(self, attrs):
    #     print("phone")
