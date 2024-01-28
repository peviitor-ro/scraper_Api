from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginRegisterView.as_view()),
    path('authorized/<str:token>', views.Authorized.as_view()),
]