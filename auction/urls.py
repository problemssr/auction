from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view()),
    path('message/', views.MessageView.as_view()),
    path('news/', views.NewsView.as_view()),
    path('topic/', views.TopicView.as_view()),
    path('news/<int:pk>/', views.NewsDetailView.as_view()),
]
