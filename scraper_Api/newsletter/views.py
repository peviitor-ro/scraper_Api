
from django.db.models import Q
from rest_framework import generics, views
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Users, Newsletter

from jobs.models import Job
from .serializer import NewsletterSerializer, UserSerializer


@permission_classes([AllowAny])
class SubscribeView(generics.CreateAPIView):

    serializer_class = UserSerializer

    def post(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)



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


# for testing purposes
@permission_classes([AllowAny])
class RecommendedJobsView(APIView):


    def post(self, request):
        email = request.data.get('email')
        try:
            user = Users.objects.get(email=email)
            newsletter = Newsletter.objects.get(email=user)

            filter_search = Q(published=False)

            if newsletter.job_title:
                filter_search &= Q(job_title__icontains=newsletter.job_title)

            if newsletter.city:
                cities = newsletter.city.split(",")
                filter_search &= Q(city__in=cities)

            if newsletter.company:
                companies = newsletter.company.split(",")
                filter_search &= Q(company__company__in=companies)

            if newsletter.job_type:
                filter_search &= Q(remote__icontains=newsletter.job_type)

            jobs = Job.objects.filter(filter_search)[::10]

            #send_newsletter_mail(newsletter.email, [{"title": job.job_title, "link": job.job_link} for job in jobs])
            response = [{"title": job.job_title, "link": job.company.company} for job in jobs]
            return Response(response)
        except Users.DoesNotExist:
            return Response('error User with this email does not exist')
        except Newsletter.DoesNotExist:
            return Response('error: No newsletter subscription found for this user')
