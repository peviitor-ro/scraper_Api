
from asgiref.sync import async_to_sync

from rest_framework_simplejwt.tokens import AccessToken
from users.models import CustomUser
from channels.layers import get_channel_layer
from channels.generic.websocket import WebsocketConsumer
import json
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Notification
from company.models import Company


def send_notification(user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}', {"type": "send_event", "message": {"message": [message]}})


@receiver(post_save, sender=Notification)
def new_notification(sender, instance, created, **kwargs):
    if created:
        send_notification(instance.user, instance.message)


@receiver(pre_delete, sender=Company)
def delete_company_data(sender, instance, **kwargs):
    # get all users associated with the company
    users = CustomUser.objects.filter(company=instance)

    # send a notification to each user
    for user in users:
        Notification.objects.create(
            user=user, message=f"Company {instance.company} has been deleted")


class NotificationConsumer(WebsocketConsumer):

    def connect(self):
        token = self.scope['query_string'].decode().split('=')[1]

        try:
            access_token = AccessToken(token)
            user = access_token.payload['user_id']
            self.user = CustomUser.objects.get(id=user)
            self.room_group_name = f'notifications_{self.user.id}'
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name)
            self.accept()

            notification = Notification.objects.filter(
                user=self.user)
            self.send(text_data=json.dumps(
                {"message": [n.message for n in notification]}))
        except Exception:
            self.close()

    def disconnect(self, code):
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name, self.channel_name)
        except:
            pass

    def send_event(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
