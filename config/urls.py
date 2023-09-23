from django.urls import path, include

urlpatterns = [
    path('', include('common.health_check.urls')),
]
