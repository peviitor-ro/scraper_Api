from django.urls import path
from . import views

urlpatterns = [
    path('get/', views.GetJobData.as_view()),
    path('add/', views.AddScraperJobs.as_view()),
    path('edit/', views.EditJob.as_view()),
    path('delete/', views.DeleteJob.as_view()),
    path('sync/', views.SyncronizeJobs.as_view()),
    path('publish/', views.PublishJob.as_view()),
    path('flush/', views.flush_and_populate.as_view()),
]

