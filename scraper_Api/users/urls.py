from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginRegisterView.as_view()),
    path('get_token', views.GetToken.as_view()),
    path('update', views.UpdateUser.as_view()),
    path('refresh', views.RefreshTokenView.as_view()),
    path('authorized/<str:token>', views.Authorized.as_view()),
    path('user/companies', views.UsersCompany.as_view()),
]