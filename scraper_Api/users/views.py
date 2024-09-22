from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string

from .serializer import UserSerializer, UserUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from dotenv import load_dotenv
import os

User = get_user_model()
load_dotenv()


@permission_classes([AllowAny])
class LoginRegisterView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        user = request.data.get('email')

        if not user:
            return Response(status=400)
        
        try:
            user = User.objects.get(email=user)
            refresh = RefreshToken.for_user(user)
            self.send_authorization_mail(user, refresh.access_token)
            return Response(status=200)
        
        except User.DoesNotExist:
            return Response(status=404)

    def send_authorization_mail(self, user, token):
        template = 'email.html'
        url = os.getenv('FRONTEND_URL')

        context = {
            'user': user,
            'token': token,
            'link': f'{url}/authorize/{token}',
        }

        subject = 'Authorization Link'
        message = render_to_string(template, context)
        email_from = 'aocpeviitor@gmail.com'
        recipient_list = [user.email, ]
        send_mail(
            subject=subject,
            message="",
            from_email=email_from,
            recipient_list=recipient_list,
            html_message=message,
        )

class AddUser(APIView):
    def post(self, request):
        if not request.user.is_superuser:
            return Response(status=401)

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(status=201)


@permission_classes([AllowAny])
class Authorized(APIView):
    def get(self, _, token):
        if not token:
            return Response(status=400)

        try:
            decoded_token = AccessToken(token)
            user_id = decoded_token.payload.get('user_id')
            user = User.objects.get(pk=user_id)
            refresh_token = RefreshToken.for_user(user)

            response = {
                "refresh": str(refresh_token),
                "access": str(decoded_token),
                "authorized": True,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            }
            return Response(response)
        except Exception:
            return Response(status=400)


@permission_classes([AllowAny])
class GetToken(APIView):
    def post(self, request, ):
        try:
            email = request.data.get('email')
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            response = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(response)

        except Exception:
            return Response(status=400)


@permission_classes([AllowAny])
class RefreshTokenView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response(status=400)

        try:
            decoded_token = RefreshToken(token)
            user_id = decoded_token.payload.get('user_id')
            User.objects.get(pk=user_id)

            response = {
                "access": str(decoded_token.access_token),
            }
            return Response(response)
        except Exception:
            return Response(status=400)


class UpdateUser(APIView):
    def post(self, request):
        if not request.user.is_superuser:
            return Response(status=401)

        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.update(request.data)

        return response

# TODO: Add permission to this view


class UserDetails(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=200)

    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.update(request.data, user)

        return response


class UsersCompany(APIView):
    serializer_class = UserUpdateSerializer

    def get(self, request):
        user = request.user
        user_get = request.GET.get('user')

        companies = list(user.company.all().order_by(
            'company').values('company'))
        scrapers = list(user.scraper.all().order_by(
            'name').values('name'))

        if user_get:
            user_get = User.objects.get(email=user_get)
            user_get_companise = user_get.company.all().values()
            user_get_scrapers = user_get.scraper.all().values()

            for company in companies:
                company['selected'] = user_get_companise.filter(
                    company=company['company']).exists()
                
            for scraper in scrapers:
                scraper['selected'] = user_get_scrapers.filter(
                    name=scraper['name']).exists()

        users = User.objects.all().filter(is_superuser=False).order_by('email').values(
            'email', 'is_staff', 'is_superuser').exclude(email=user.email)

        response = {
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "companies": companies,
            "scrapers": scrapers,
            "users": users,
        }
        return Response(response)

    def post(self, request):
        data = request.data
        serializer = UserUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_superuser:
            response = serializer.update(data=data)
            return response

        elif request.user.is_staff:
            try:
                data.pop('is_staff')
                data.pop('is_superuser')
            except KeyError:
                pass
            response = serializer.update(data=data)
            return response

        return Response(status=401)
    
class DeleteUser(APIView):
    def post(self, request):
        user = request.user
        user_delete = request.data.get('email')
        if user.is_superuser:
            user_delete = User.objects.get(email=user_delete)
            # user_delete.delete()
            return Response(status=200)
        return Response(status=401)
