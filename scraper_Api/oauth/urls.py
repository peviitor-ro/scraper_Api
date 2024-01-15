from django.urls import path
from django.contrib.auth import views as auth_views 
from .views import LoginView

urlpatterns = [
    path('homepage/', LoginView.as_view(template_name='dist/index.html')),
    path('logout/', auth_views.LogoutView.as_view()),
]
