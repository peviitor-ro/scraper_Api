from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Notification


@api_view(['POST'])
def mark_notifications_read(request):
    messages = Notification.objects.filter(
        user=request.user)
    for message in messages:
        message.delete()
    return Response({"status": "success"})
