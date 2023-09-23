# open_ai/urls.py

from django.urls import path
from . import views
from rest_framework import routers

app_name = 'open_ai'

router = routers.DefaultRouter()

urlpatterns = [
    path('test', views.completion)
]
