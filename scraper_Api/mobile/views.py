from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.pagination import CustomPagination
from .serializer import JobSerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
import json

from jobs.models import Job


@permission_classes([AllowAny])
class GetJobView(APIView):
    serializer_class = JobSerializer
    pagination_class = CustomPagination

    def get(self, request):
        search_query = request.GET.get("search") or None
        cities = request.GET.get("cities") or None
        counties = request.GET.get("counties") or None
        remote = request.GET.get("remote") or None

        filter_search = Q(published=True)

        if search_query:
            filter_search &= Q(job_title__icontains=search_query)

        if cities and counties:
            cities_lst = cities.split(",")
            counties_lst = counties.split(",")
            
            for city, county in zip(cities_lst, counties_lst):
                filter_search &= Q(city__icontains=city) & Q(county__icontains=county)

            filter_search |= Q(city__in=cities_lst) & Q(county__in=counties_lst)

        if remote:
            remote_lst = remote.split(",")
            filter_search &= Q(remote__in=remote_lst)

        queryset = Job.objects.filter(filter_search)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@permission_classes([AllowAny])
class GetTotalJobs(APIView):
    def get(self, _):
        total_jobs = Job.objects.filter(published=True).count()
        return Response({"total": total_jobs})
