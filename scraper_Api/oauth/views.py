from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from social_django.models import UserSocialAuth
from rest_framework.authtoken.models import Token
from django.contrib.auth import views as auth_views


class LoginView(auth_views.LoginView):
    template_name = 'dist/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:

            token = Token.objects.get_or_create(user=request.user)
            response = redirect('http://localhost:3000/oauth/', permanent=True)
            # set cookie

            response.set_cookie('token', token[0].key)
            return response

        else:
            return render(request, self.template_name, status=401)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social'] = UserSocialAuth.objects.get(
            user=self.request.user).extra_data
        return context
