from rest_framework import serializers
from .models import Newsletter, Users
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = Users
    fields = ['email']


class NewsletterSerializer(serializers.ModelSerializer):
  email = UserSerializer(read_only=True)

  class Meta:
    model = Newsletter
    fields = ['email', 'job_title', 'city', 'job_type', 'company']

  def create(self, validated_data):
    email = validated_data.get('email')
    user = get_object_or_404(Users, email=email)
    data_search = validated_data.get('data') or {}

    newsletter, created = Newsletter.objects.get_or_create(email=user)
    if not created and data_search:
      newsletter.clean_data()

    for k, v in data_search.items():
      setattr(newsletter, k, v)
    newsletter.save()

    return newsletter

