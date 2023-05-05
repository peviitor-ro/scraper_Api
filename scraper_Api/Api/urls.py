from django.urls import path
from . import views

urlpatterns = [
    path('add/' , views.AddView.as_view()),
    path('remove/' , views.RemoveView.as_view()),
    path('<path>/' , views.ScraperView.as_view()),
]


