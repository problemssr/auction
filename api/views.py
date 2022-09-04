from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import BaseFilterBackend
from rest_framework import serializers
from django.forms import model_to_dict
from rest_framework.response import Response
import re
import random
import uuid
from api.Serializer.account import MessageSerializer, LoginSerializer
from api import models


class NewsModelSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()

    class Meta:
        model = models.News
        fields = ['id', 'cover', 'content', 'topic', "user", 'favor_count']

    def get_user(self, obj):
        # return {'id': obj.user_id, 'nickname': obj.user.nickname, 'avatar': obj.user.avatar}
        return model_to_dict(obj.user, fields=['id', 'nickname', 'avatar'])

    def get_topic(self, obj):
        if not obj.topic:
            return
        # return {'id': obj.topic_id, 'title': obj.topic.title}
        return model_to_dict(obj.topic, fields=['id', 'title'])


"""
class NewsView(APIView):
    def get(self, request, *args, **kwargs):
        min_id = request.query_params.get('min_id')
        max_id = request.query_params.get('max_id')
        if min_id:
            queryset = models.News.objects.filter(id__lt=min_id).order_by('-id')[0:10]
        elif max_id:    
            queryset = models.News.objects.filter(id__gt=max_id).order_by('id')[0:10]
        else:
            queryset = models.News.objects.all().order_by('-id')[0:10]
        ser = NewsModelSerializer(instance=queryset, many=True)
        return Response(ser.data, status=200)
"""


############################## 动态列表 #############################

class NewsPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 50
    limit_query_param = 'limit'
    offset_query_param = 'offset'

    def get_offset(self, request):
        return 0

    def get_paginated_response(self, data):
        return Response(data)


class MinFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        min_id = request.query_params.get('min_id')
        if min_id:
            return queryset.filter(id__lt=min_id).order_by('-id')
        return queryset


class MaxFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        max_id = request.query_params.get('max_id')
        if max_id:
            return queryset.filter(id__gt=max_id).order_by('id')
        return queryset


class NewsView(ListAPIView):
    serializer_class = NewsModelSerializer
    queryset = models.News.objects.all().order_by('-id')
    pagination_class = NewsPagination
    filter_backends = [MinFilterBackend, MaxFilterBackend]


# ############################# 话题  #############################
class TopicModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Topic
        fields = "__all__"


class TopicView(ListAPIView):
    serializer_class = TopicModelSerializer
    queryset = models.Topic.objects.all().order_by('-id')

    pagination_class = NewsPagination
    filter_backends = [MinFilterBackend, MaxFilterBackend]


############################## 动态详细 #############################

class NewsDetailModelSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = models.News
        # fields = "__all__"
        exclude = ['cover', ]

    def get_images(self, obj):
        detail_queryset = models.NewsDetail.objects.filter(news=obj)
        # return [row.cos_path for row in detail_queryset]
        # return [{'id':row.id,'path':row.cos_path} for row in detail_queryset]
        return [model_to_dict(row, ['id', 'cos_path']) for row in detail_queryset]


class NewsDetailView(RetrieveAPIView):
    serializer_class = NewsDetailModelSerializer
    queryset = models.News.objects


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
        print("随机嘛", random_code)
        # 5.把验证码+手机号保留（30s过期） conn.set("15944445555","1234",ex=40)
        from django_redis import get_redis_connection
        conn = get_redis_connection()
        conn.set(phone, random_code)

        return Response({"status": True, 'message': '发送成功'})
