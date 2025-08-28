
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from requests.auth import HTTPBasicAuth

from .constants import JOB_SORT_OPTIONS

from .models import Job
from company.models import Company, DataSet, Source
from utils.pagination import CustomPagination
from .serializer import (
    GetJobSerializer,
    JobAddSerializer,
    JobAEditSerializer,
)

from company.serializers import CompanySerializer
from django.utils.timezone import datetime
from pysolr import Solr
import os

JOB_NOT_FOUND = {"message": "Job not found"}
url = os.getenv("DATABASE_SOLR") + "/solr/jobs"
username = os.getenv("DATABASE_SOLR_USERNAME")
password = os.getenv("DATABASE_SOLR_PASSWORD")


class JobView(object):
    def update(self, jobs, attribute):
        if isinstance(jobs, list) and len(jobs) > 0 and hasattr(Job, attribute):
            for job in jobs:
                job_link = self.transform_data(job.get("job_link"))
                job_obj = Job.objects.get(job_link=job_link)

                if not job_obj:
                    return Response(JOB_NOT_FOUND)

                setattr(job_obj, attribute, not getattr(job_obj, attribute))
                job_obj.date = datetime.now()
                job_obj.publish()
                job_obj.save()

            return Response({"message": f"Job {attribute}"})
        else:
            return Response(status=400)

    def transformed_jobs(self, jobs):
        data = []
        if isinstance(jobs, list) and len(jobs) > 0:
            for job in jobs:
                source = job.get("source")
                job_obj = {
                    "job_link": self.transform_data(job.get("job_link")),
                    "job_title": self.transform_data(job.get("job_title")),
                    "country": self.transform_data(job.get("country")),
                    "city": self.transform_data(job.get("city")),
                    "county": self.transform_data(job.get("county")),
                    "remote": self.transform_data(job.get("remote")),
                    "company": self.transform_data(job.get("company")).title(),
                }

                if source:
                    source_obj = Source.objects.filter(sursa=source).first()
                    if source_obj:
                        job_obj["source"] = source_obj.id
                    else:
                        job_obj["source"] = None
                data.append(job_obj)
        return data

    def transform_data(self, data):
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            data_string = ",".join(
                [str(item).strip() for item in data if isinstance(item, str)]
            )
            return data_string
        else:
            return ""


class AddScraperJobs(APIView, JobView):
    def post(self, request):
        try:
            jobs = self.transformed_jobs(request.data)

            if not jobs:
                return Response(status=400)

            posted_jobs = []

            
            for job in jobs:
                company = self.transform_data(job.get("company")).title()

                company_obj = {"company": company}

                if job.get("source"):
                    company_obj["source"] = job.get("source")

                company_serializer = CompanySerializer(data=company_obj,)

                company_serializer.is_valid(raise_exception=True)
                company_instance = company_serializer.save()

                user = request.user
                user.company.add(company_instance)

                job["company"] = company_instance.id

                job_link = self.transform_data(job.get("job_link"))


                if not Job.objects.filter(job_link=job_link).exists():

                    job_serializer = JobAddSerializer(
                        data=job, context={"request": request})

                    job_serializer.is_valid(raise_exception=True)

                    job_serializer.save()

                    posted_jobs.append(job_serializer.data)

            current_date = datetime.now()

            company_instance = Company.objects.filter(company=company).first()
            jobs = Job.objects.filter(company=company_instance).count()

            DataSet.objects.update_or_create(
                company=company_instance, date=current_date, defaults={
                    "data": jobs}
            )
            
            return Response(posted_jobs)
        except Exception as e:
            print(e)
            return Response(status=400)

    @property
    def delete(self):
        scraper_data = self.transformed_jobs(self.request.data)
        if isinstance(scraper_data, list) and len(scraper_data) > 0:
            company_obj = Company.objects.filter(
                company=self.transform_data(scraper_data[0].get("company"))
            ).first()
            database_jobs = Job.objects.filter(company=company_obj.id).values()
            scraper_data = [
                self.transform_data(job.get("job_link")) for job in scraper_data
            ]
            database_jobs = [job.get("job_link") for job in database_jobs]
            to_delete = [
                job for job in database_jobs if job not in scraper_data]

            for job in to_delete:
                Job.objects.filter(job_link=job).first().delete()


class GetJobData(APIView):
    serializer_class = GetJobSerializer
    pagination_class = CustomPagination

    def get(self, request):
        company = request.GET.get("company",)
        search = request.GET.get("search") or ""
        order_query = request.GET.get("order") or "all"
        order_by = JOB_SORT_OPTIONS.get(order_query)
        user = request.user
        user_companies = user.company.all()

        if user_companies.filter(company=company.title()).exists():
            company = get_object_or_404(Company, company=company.title())
            queryset = Job.objects.filter(
                company=company.id, job_title__icontains=search
            ).order_by(order_by)
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(result_page, many=True)

            jobs = []
            for job in serializer.data:
                job["company"] = company.company
                job["country"] = [
                ] if not job["country"] else job["country"].split(",")
                job["city"] = [] if not job["city"] else job["city"].split(",")
                job["county"] = [] if not job["county"] else job["county"].split(
                    ",")

                jobs.append(job)

            return paginator.get_paginated_response(jobs)
        else:
            return Response(status=401)

    def post(self, request):
        company = request.data.get("company")
        user = request.user
        user_companies = user.company.all()

        if user_companies.filter(company=company.title()).exists():
            company = get_object_or_404(Company, company=company.title())
            queryset = Job.objects.filter(company=company.id)
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(result_page, many=True)

            jobs = []
            for job in serializer.data:
                job["company"] = company.company
                job["country"] = job["country"].split(",")
                job["city"] = job["city"].split(",")
                job["county"] = job["county"].split(",")

                jobs.append(job)

            return paginator.get_paginated_response(jobs)
        else:
            return Response(status=401)


class EditJob(APIView, JobView):
    def post(self, request):
        jobs = self.transformed_jobs(request.data)
        for job in jobs:
            try:
                company = request.user.company.get(
                    company=self.transform_data(job.get("company")).title())
                job["company"] = company.id

                serializer = JobAEditSerializer(
                    data=job, context={"request": request})
                serializer.is_valid(raise_exception=True)
                serializer.save()

            except Exception:
                return Response(status=404)

        return Response({"message": "Job edited"})


class DeleteJob(APIView, JobView):
    def post(self, request):
        jobs = self.transformed_jobs(request.data)

        if not jobs:
            return Response(status=400)

        for job in jobs:
            try:
                company = request.user.company.get(
                    company=self.transform_data(job.get("company")).title())
                job_link = self.transform_data(job.get("job_link"))
                job_obj = Job.objects.get(job_link=job_link, company=company)

                if not job_obj:
                    return Response(JOB_NOT_FOUND)

                job_obj.delete()
            except Exception:
                return Response(status=404)

        return Response({"message": "Job deleted"})


class PublishJob(APIView, JobView):
    def post(self, request):
        response = self.update(request.data, "published")
        return response


class SyncronizeJobs(APIView):
    def post(self, request):
        company = request.data.get("company")

        if not company:
            return Response(status=400)

        solr = Solr(url=url, auth=HTTPBasicAuth(username, password), timeout=60)
        solr.delete(q=f"company:{company}")
        solr.commit(expungeDeletes=True)

        company_instance = get_object_or_404(Company, company=company)
        jobs = Job.objects.filter(company=company_instance, published=True)

        for job in jobs:
            job.publish()

        return Response({"message": "Jobs synchronized"})
    

class flush_and_populate(APIView):
    solr = Solr(url=url, auth=HTTPBasicAuth(username, password), timeout=5)
    def post(self, request):
        user = request.user

        if not user.is_superuser:
            return Response(status=401)
        
        try:
            
            jobs = Job.objects.filter(published=True)
            
            jobs = [
                {
                    "id": job.getJobId,
                    "job_link": job.job_link,
                    "job_title": job.job_title,
                    "company": job.company.company,
                    "country": job.country.split(","),
                    "city": job.city.split(","),
                    "county": job.county.split(","),
                    "remote": job.remote.split(","),
                }
                for job in jobs
            ]

            self.solr.delete(q="*:*")
            self.solr.commit(expungeDeletes=True)

            if jobs:
                self.solr.add(jobs)
                self.solr.commit(expungeDeletes=True)

            return Response(200)
        except Exception as e:
            return Response(status=400)

