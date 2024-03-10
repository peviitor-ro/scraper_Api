from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .serializer import UserSerializer, UserUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()

@permission_classes([AllowAny])
class LoginRegisterView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        self.send_authorization_mail(user, refresh.access_token)

        return Response(status=201)
    
    def send_authorization_mail(self, user, token):
        subject = 'Authorization Link'
        message = f'Here is your authorization link: http://localhost:3000/authorize/{token}'
        email_from = 'test@test.com'
        recipient_list = [user.email, ]
        send_mail(subject, message, email_from, recipient_list)
    
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


        
