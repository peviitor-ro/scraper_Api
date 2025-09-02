from django.db.models import Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response

from .constants import COMPANY_SORT_OPTIONS
from .serializers import CompanySerializer
from utils.pagination import CustomPagination
from company.models import DataSet
from datetime import datetime, timedelta
from .serializers import DataSetSerializer

from jobs.models import Job
from company.models import Company
from pysolr import Solr
from requests.auth import HTTPBasicAuth

from dotenv import load_dotenv
import os
load_dotenv()


class GetCompanyData(APIView):
    serializer_class = CompanySerializer
    pagination_class = CustomPagination

    def get(self, request):

        order_query = request.GET.get("order", "name_asc")
        order_by = COMPANY_SORT_OPTIONS.get(order_query)
        search_query = request.GET.get("search") or ""

        model = Company.objects.all()
        if "access_" in order_query:
            model = request.user.company
            order_by = COMPANY_SORT_OPTIONS.get(order_query.replace("access_", ""))


        if order_by in ["jobs_count", "-jobs_count"]:
            queryset = (model.annotate(jobs_count=Count(
                "jobs")).order_by(order_by))

        elif order_by in ["un_published_jobs_count", "-un_published_jobs_count"]:
            queryset = (
                model.annotate(
                    un_published_jobs_count=Count(
                        "jobs", filter=Q(jobs__published=True))
                ).order_by(order_by)
            )
        else:
            queryset = (
                model.filter(
                    Q(company__icontains=search_query) | Q(
                        scname__icontains=search_query)
                )
                .order_by(order_by)
            )

        paginator = self.pagination_class()

        result_page = paginator.paginate_queryset(queryset, request)

        serializer = self.serializer_class(
            result_page, many=True, context={"request": request})

        return paginator.get_paginated_response(serializer.data)


class AddCompany(APIView):
    serializer_class = CompanySerializer

    def post(self, request):
        validated_data = request.data
        user = request.user

        companies = Company.objects.filter(
            company=validated_data.get("company"))

        if companies.exists():
            return Response(status=400)

        serializer = self.serializer_class(data=validated_data, context={"request": request})

        if serializer.is_valid():
            company = serializer.save()
            user.company.add(company)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class UpdateCompany(APIView):
    serializer_class = CompanySerializer

    def post(self, request):
        user = request.user
        company = request.data.get("company")
       
        try:
            update = request.data.get("update") or company
            user_companies = user.company.get(company=company.title())
            serializer = self.serializer_class(
                user_companies, data=update, partial=True, context={"request": request})

            if serializer.is_valid():
                serializer.save()
                return Response(status=200)
        except Company.DoesNotExist:
            return Response(status=400)



class DeleteCompany(APIView):
    def post(self, request):
        user = request.user

        if not user.is_superuser and not user.is_staff:
            return Response(status=401)

        company = request.data.get("company")
        user = request.user
        user_companies = user.company.all()

        if user_companies.filter(company=company.title()).exists():
            company = user_companies.get(company=company.title())
            company.delete()
            return Response(status=200)
        else:
            return Response(status=401)


class ClearCompany(APIView):

    def post(self, request):
        company = request.data.get("company")
        user = request.user
        user_companies = user.company.all()

        if user_companies.filter(company=company.title()).exists():
            company = user_companies.get(company=company.title())
            self.clear(company)

            return Response(status=200)
        else:
            return Response(status=401)

    def clear(self, company):
        jobs = Job.objects.filter(company=company)

        for job in jobs:
            job.published = False
            job.save()

        url = os.getenv("DATABASE_SOLR") + "/solr/jobs"
        username = os.getenv("DATABASE_SOLR_USERNAME")
        password = os.getenv("DATABASE_SOLR_PASSWORD")

        solr = Solr(url=url, auth=HTTPBasicAuth(username, password), timeout=60)
        solr.delete(q=f"company:{company.company}")
        solr.commit(expungeDeletes=True)


class DataSetView(APIView):
    def get(self, request, id):
        company = Company.objects.filter(id=id).first()
        company = request.user.company.filter(company=company).first()

        if not company:
            return Response(status=401)

        # get last 30 days
        current_date = datetime.now()
        last_30_days = current_date - timedelta(days=30)
        data = DataSet.objects.filter(
            company=company, date__gte=last_30_days).order_by('date')

        serializer = DataSetSerializer(data, many=True)
        return Response(serializer.data)


