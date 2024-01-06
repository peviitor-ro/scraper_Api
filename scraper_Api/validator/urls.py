from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.ScraperValidator.as_view()),
    path('get/', views.GetCompanyData.as_view()),
    path('edit/', views.EditJob.as_view()),
]

