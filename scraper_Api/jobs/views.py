
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

from .constants import JOB_SORT_OPTIONS

from .models import Job
from company.models import Company, DataSet
from utils.pagination import CustomPagination
from .serializer import (
    GetJobSerializer,
    JobAddSerializer,
    JobAEditSerializer,
)

from company.serializers import CompanySerializer

JOB_NOT_FOUND = {"message": "Job not found"}


class JobView(object):
    def update(self, jobs, attribute):
        if isinstance(jobs, list) and len(jobs) > 0 and hasattr(Job, attribute):
            for job in jobs:
                job_link = self.transform_data(job.get("job_link"))
                job_obj = Job.objects.get(job_link=job_link)

                if not job_obj:
                    return Response(JOB_NOT_FOUND)

                setattr(job_obj, attribute, not getattr(job_obj, attribute))
                job_obj.save()

            return Response({"message": f"Job {attribute}"})
        else:
            return Response(status=400)

    def transformed_jobs(self, jobs):
        data = []
        if isinstance(jobs, list) and len(jobs) > 0:
            for job in jobs:
                job_obj = {
                    "job_link": self.transform_data(job.get("job_link")),
                    "job_title": self.transform_data(job.get("job_title")),
                    "country": self.transform_data(job.get("country")),
                    "city": self.transform_data(job.get("city")),
                    "county": self.transform_data(job.get("county")),
                    "remote": self.transform_data(job.get("remote")),
                    "company": self.transform_data(job.get("company")).title(),
                }
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
        jobs = self.transformed_jobs(request.data)

        if not jobs:
            return Response(status=400)
        
        posted_jobs = []

        for job in jobs:
            company = self.transform_data(job.get("company")).title()

            company_serializer = CompanySerializer(data={"company": company},)

            company_serializer.is_valid(raise_exception=True)
            instance = company_serializer.save()

            user = request.user
            user.company.add(instance)

            job["company"] = instance.id

            job_serializer = JobAddSerializer(data=job, context={"request": request})

            job_serializer.is_valid(raise_exception=True)
            job_serializer.save()

            posted_jobs.append(job_serializer.data)

        current_date = datetime.now()
        DataSet.objects.update_or_create(
            company=instance, date=current_date, defaults={"data": len(posted_jobs)}
        )

        return Response(posted_jobs)


    @property
    def delete(self):
        scraper_data = self.request.data

        if isinstance(scraper_data, list) and len(scraper_data) > 0:
            company_obj = Company.objects.filter(
                company=self.transform_data(scraper_data[0].get("company"))
            ).first()
            database_jobs = Job.objects.filter(company=company_obj.id).values()
            scraper_data = [
                self.transform_data(job.get("job_link")) for job in scraper_data
            ]
            database_jobs = [job.get("job_link") for job in database_jobs]
            to_delete = [job for job in database_jobs if job not in scraper_data]

            for job in to_delete:
                Job.objects.filter(job_link=job).delete()




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
            company=company.id , job_title__icontains=search
            ).order_by(order_by)
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(result_page, many=True)

            jobs = []
            for job in serializer.data:
                job["company"] = company.company
                job["country"] = [] if not job["country"] else job["country"].split(",")
                job["city"] = [] if not job["city"] else job["city"].split(",")
                job["county"] = [] if not job["county"] else job["county"].split(",")

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
                company = request.user.company.get(company=self.transform_data(job.get("company")).title())
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
                company = request.user.company.get(company=self.transform_data(job.get("company")).title())
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
