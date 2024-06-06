
from django.db.models import Q
from django.template.loader import render_to_string
from rest_framework import generics, views
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Users, Newsletter
from django.shortcuts import get_object_or_404

from jobs.models import Job
from .serializer import NewsletterSerializer, UserSerializer
from django.core.mail import send_mail


@permission_classes([AllowAny])
class SubscribeView(generics.CreateAPIView):

    serializer_class = UserSerializer

    def perform_create(self, serializer):
        serializer.save()


@permission_classes([AllowAny])
class UnSubscribeView(views.APIView):

    def post(self, request):
        data = request.data
        email = data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Users.objects.get(email=email)
            user.delete()
            return Response({'message': 'Unsubscribed successfully'}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)


@permission_classes([AllowAny])
class SaveNewsletterDataView(views.APIView):

    def post(self, request):
        data = request.data

        serializer = NewsletterSerializer(data=data, partial=True)
        serializer.is_valid()
        serializer.create(data)

        return Response({'message': 'Subscribed successfully'}, status=status.HTTP_201_CREATED)


def send_newsletter_mail(email, recommended_jobs):
    template = 'newsletter.html'

    context = {
        'email': email,
        'recommended_jobs': recommended_jobs,
    }

    subject = 'Jop postings update'
    message = render_to_string(template, context)
    email_from = 'cristi_olteanu@outlook.com'
    recipient_list = [email.email, ]
    send_mail(
        subject=subject,
        message="",
        from_email=email_from,
        recipient_list=recipient_list,
        html_message=message,
    )


@permission_classes([AllowAny])
class RecommendedJobsView(APIView):


    def post(self, request):
        email = request.data.get('email')
        try:
            user = Users.objects.get(email=email)
            newsletter = Newsletter.objects.get(email=user)

            title_condition = Q(job_title__icontains=newsletter.job_title)
            exact_title_condition = Q(job_title=newsletter.job_title)
            city_condition = Q(city__icontains=newsletter.city)
            company_condition = Q(company__company__icontains=newsletter.company)
            remote_condition = Q(remote__icontains=newsletter.job_type)
            published_condition = Q(published=True)

            jobs = Job.objects.filter(
                (exact_title_condition | title_condition | city_condition | company_condition | remote_condition
                 ) & published_condition)

            #send_newsletter_mail(newsletter.email, [{"title": job.job_title, "link": job.job_link} for job in jobs])
            return Response([job.job_title for job in jobs])
        except Users.DoesNotExist:
            return Response('error User with this email does not exist')
        except Newsletter.DoesNotExist:
            return Response('error: No newsletter subscription found for this user')
