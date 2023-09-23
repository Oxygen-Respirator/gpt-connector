from django.urls import path, include

urlpatterns = [
    path('', include('health_check.urls')),
    path('api/', include('open_ai.urls'))
]
