from django.urls import path
from . import views
from .views import DataSetView as DataSet

urlpatterns = [
    path('', views.GetCompanyData.as_view()),
    path('delete/', views.DeleteCompany.as_view()),
    path('clear/', views.ClearCompany.as_view()),
    path('dataset/<company>/', DataSet.as_view()),
]