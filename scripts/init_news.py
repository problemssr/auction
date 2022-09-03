"""
初始化动态表，在动态表中添加一些数据，方便操作
"""
import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auction.settings")
django.setup()

from api import models

for i in range(1,37):
    news_object = models.News.objects.create(
        cover="https://xiaohuazhuo.com/static/img/logo.20153c84.png",
        content="还有{0}天就放假".format(i),
        topic_id=1,
        user_id=1
    )

    models.NewsDetail.objects.create(
        key="08a9daei1578736867828.png",
        cos_path="https://xiaohuazhuo.com/static/img/logo.20153c84.png",
        news=news_object
    )