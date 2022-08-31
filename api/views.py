from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
import re
import random
from rest_framework.exceptions import ValidationError


# Create your views here.
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        return Response({"status": True})


def phone_validator(value):
    if not re.match(r"^(1[3|4|5|6|7|8|9])\d{9}$", value):
        raise ValidationError("手机格式错误")


class MessageSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])

    # def validate_phone(self, attrs):
    #     print("phone")


class MessageView(APIView):
    def get(self, request, *args, **kwargs):
        """
        发送手机短信验证码
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 1.获取手机号
        # phone = request.query_params.get("phone")
        # print(phone)

        # 2.手机格式校验

        ser = MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response({'status':False,'message':'手机格式错误'})

        phone=ser.validated_data.get('phone')
        # 3.生成随机验证码
        random_code=random.randint(1000,9999)
        # 4.验证码发送到手机上，购买服务器进行发送短信：腾讯云
        from django_redis import get_redis_connection
        conn = get_redis_connection()
        conn.set(phone,random_code,ex=30)

        return Response({"status": True,'message':'发送成功'})
        # 5.把验证码+手机号保留（30s过期） conn.set("15944445555","1234",ex=40)

