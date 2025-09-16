from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.pagination import CustomPagination
from .serializer import JobSerializer, CompanySerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from jobs.models import Job
from company.models import Company


@permission_classes([AllowAny])
class GetJobView(APIView):
    serializer_class = JobSerializer
    pagination_class = CustomPagination

    def get(self, request):
        search_query = request.GET.get("search") or None
        cities = request.GET.get("cities") or None
        counties = request.GET.get("counties") or None
        companies = request.GET.get("companies") or None
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
        elif cities:
            cities_lst = cities.split(",")
            filter_search &= Q(city__in=cities_lst)
        elif counties:
            counties_lst = counties.split(",")
            filter_search &= Q(county__in=counties_lst)

        if companies:
            companies_lst = companies.split(",")
            for company in companies_lst:
                company_id = Company.objects.get(company=company).id
                filter_search &= Q(company=company_id)
            

        if remote:
            remote_lst = remote.split(",")
            filter_search &= Q(remote__in=remote_lst)

        queryset = Job.objects.filter(filter_search)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

@permission_classes([AllowAny])
class GetCompanies(APIView):
    serializer_class = CompanySerializer
    pagination_class = CustomPagination
    def get(self, _):
        search_query = self.request.GET.get("search") or None
        filter_search = Q()

        if search_query:
            filter_search &= Q(company__icontains=search_query)

        companies = Company.objects.filter(filter_search)
        paginator = self.pagination_class()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(companies, self.request)
        companies = self.serializer_class(result_page, many=True)
        return paginator.get_paginated_response(companies.data)

@permission_classes([AllowAny])
class GetTotalJobs(APIView):
    def get(self, _):
        total_jobs = Job.objects.filter(published=True).count()
        return Response({"total": total_jobs})
    

@permission_classes([AllowAny])
class CheckSavedJobsView(APIView):
    def post(self, request):
        job_ids = request.data.get("ids", [])
        
        if not isinstance(job_ids, list):
            return Response({"error": "job_ids must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_jobs = Job.objects.filter(id__in=job_ids, published=True).values_list('id', flat=True)
        existing_job_ids = list(existing_jobs)

        return Response({"existing_job_ids": existing_job_ids}, status=status.HTTP_200_OK)
