from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import re
import random
import uuid
from api.Serializer.account import MessageSerializer, LoginSerializer
from api import models


# Create your views here.
class LoginView(APIView):
    """
    1. 校验手机号是否合法
    2. 校验验证码，redis
        - 无验证码
        - 有验证码，输入错误
        - 有验证码，成功

    4. 将一些信息返回给小程序
    """

    def post(self, request, *args, **kwargs):
        # print(request.data)
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"status": False, 'message': '验证码错误'})

        # 3. 去数据库中获取用户信息（获取/创建）
        phone = ser.validated_data.get('phone')
        user_obj, flag = models.UserInfo.objects.get_or_create(phone=phone)
        user_obj.token = str(uuid.uuid4())
        user_obj.save()
        # 笨重
        # user = models.UserInfo.objects.filter(phone=phone).first()
        # if not user:
        #     models.UserInfo.objects.create(phone=phone, token=str(uuid.uuid4()))
        # else:
        #     user.token = str(uuid.uuid4())
        #     user.save()

        return Response({"status": True, "data": {"token": user_obj.token, "phone": phone}})


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
            return Response({'status': False, 'message': '手机格式错误'})

        phone = ser.validated_data.get('phone')
        # 3.生成随机验证码
        random_code = random.randint(1000, 9999)
        # 4.验证码发送到手机上，购买服务器进行发送短信：腾讯云
        # 略
        print("随机嘛",random_code)
        # 5.把验证码+手机号保留（30s过期） conn.set("15944445555","1234",ex=40)
        from django_redis import get_redis_connection
        conn = get_redis_connection()
        conn.set(phone, random_code)

        return Response({"status": True, 'message': '发送成功'})
