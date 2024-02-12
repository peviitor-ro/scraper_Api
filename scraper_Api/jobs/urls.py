from django.urls import path
from . import views

urlpatterns = [
    # Company
    path('companies', views.GetCompanyData.as_view()),
    # Jobs
    path('jobs/get/', views.GetJobData.as_view()),
    path('add/', views.AddScraperJobs.as_view()),
    path('edit/', views.EditJob.as_view()),
    path('delete/', views.DeleteJob.as_view()),
    path('publish/', views.PublishJob.as_view()),
]

