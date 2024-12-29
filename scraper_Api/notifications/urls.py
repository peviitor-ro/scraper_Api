from django.urls import path
from .views import mark_notifications_read


urlpatterns = [
    path('read/', mark_notifications_read),
]
