from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.SubscribeView.as_view()),
    path('unsubscribe/', views.UnSubscribeView.as_view(), name='unsubscribe'),
    path('send/', views.SaveNewsletterDataView.as_view()),
    path('recommended_jobs/', views.RecommendedJobsView.as_view()),

]