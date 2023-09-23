# health_check/urls.py

from django.urls import path
from rest_framework import routers
from health_check import views

router = routers.DefaultRouter()

urlpatterns = [
    path('', views.healthCheck),
]
