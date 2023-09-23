from django.apps import AppConfig
from rest_framework import serializers, viewsets

class OpenAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domain.completion'