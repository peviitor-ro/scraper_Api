from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .serializer import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
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

        # Send email
        subject = 'Authorization Link'
        message = f'Here is your authorization link: http://localhost:3000/authorize/{refresh.access_token}'
        email_from = 'test@test.com'
        recipient_list = [user.email, ]
        send_mail(subject, message, email_from, recipient_list)
        return Response(status=201)
    
@permission_classes([AllowAny])
class Authorized(APIView):
    def ge(self, request):
        token = request.data.get('token')
        if token:
            try:
                decoded_token = RefreshToken(token)
                user_id = decoded_token.payload.get('user_id')
                User.objects.get(pk=user_id)

                response = {
                    "refresh": str(decoded_token),
                    "access": str(decoded_token.access_token),
                    "authorized": True,
                }
                return Response(response)
            except Exception as e:
                print(e)
                return Response({'error': 'Invalid token'}, status=400)
        return Response({'error': 'Token not found'}, status=400)
