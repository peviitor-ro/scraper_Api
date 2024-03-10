from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.ScraperAddView.as_view()),
    path('remove/' , views.ScraperRemoveView.as_view()),
    path('<path>/', views.ScraperListView.as_view()),
]


