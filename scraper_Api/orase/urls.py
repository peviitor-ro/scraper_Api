from django.urls import path
from .views import CityViewSet

urlpatterns = [
    path('', CityViewSet.as_view(), name='city')
]
