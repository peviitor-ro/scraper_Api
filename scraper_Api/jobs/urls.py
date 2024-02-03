from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.AddScraperJobs.as_view()),
    path('getcompanies/', views.GetCompanyData.as_view()),
    path('edit/', views.EditJob.as_view()),
    path('delete/', views.DeleteJob.as_view()),
    path('publish/', views.PublishJob.as_view()),
]

