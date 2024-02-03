from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import (
    JobAddSerializer, 
    CompanySerializer,
    GetJobSerializer,
    )
from .models import Job, Company
from django.shortcuts import get_object_or_404

JOB_NOT_FOUND = {'message': 'Job not found'}
    
class JobView(object):
    def update(self, jobs, attribute):
        if isinstance(jobs, list) and len(jobs) > 0 and hasattr(Job, attribute):
            for job in jobs:
                job_link = self.transform_data(job.get('job_link'))
                job_obj = Job.objects.get(job_link=job_link)

                if not job_obj:
                    return Response(JOB_NOT_FOUND)
                
                setattr(job_obj, attribute, not getattr(job_obj, attribute))
                job_obj.save()

            return Response({'message': f'Job {attribute}'})
        else:
            return Response(status=400)

    def transformed_jobs(self,jobs):
        data = []
        if isinstance(jobs, list) and len(jobs) > 0:
            for job in jobs:
                job_obj = {
                    "job_link": self.transform_data(job.get('job_link')),
                    "job_title": self.transform_data(job.get('job_title')),
                    "country": self.transform_data(job.get('country')),
                    "city": self.transform_data(job.get('city')),
                    "county": self.transform_data(job.get('county')),
                    "remote": self.transform_data(job.get('remote')),
                    "company":self.transform_data(job.get('company')).title()
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
            company = self.transform_data(job.get('company')).title()

            company_serializer = CompanySerializer(
                data={'company': company})

            company_serializer.is_valid(raise_exception=True)
            instance = company_serializer.save()
                
            job['company'] = instance.id

            job_serializer = JobAddSerializer(data=job, context={'request': request})

            job_serializer.is_valid(raise_exception=True)
            job_serializer.save()

            posted_jobs.append(job_serializer.data)

        return Response(posted_jobs)

    
    @property
    def delete(self):
        scraper_data = self.request.data
        
        if isinstance(scraper_data, list) and len(scraper_data) > 0: 
            company_obj = Company.objects.filter(company=self.transform_data(scraper_data[0].get('company'))).first()
            database_jobs = Job.objects.filter(company=company_obj.id).values()
            scraper_data = [self.transform_data(job.get('job_link')) for job in scraper_data]
            database_jobs = [job.get('job_link') for job in database_jobs]
            to_delete = [job for job in database_jobs if job not in scraper_data]
            
            for job in to_delete:
                Job.objects.filter(job_link=job).delete()
    
class GetCompanyData(APIView):
    def get(self, request):
        user = request.user
        user_companies = user.company.all()
        serializer = CompanySerializer(user_companies, many=True)

        return Response(serializer.data)

    def post(self, request):
        company = request.data.get('company')
        user = request.user
        user_companies = user.company.all()

        if user_companies.filter(company=company.title()).exists():
            company = get_object_or_404(Company, company=company.title())
            jobs_objects = Job.objects.filter(company=company.id)
            serializer = GetJobSerializer(jobs_objects, many=True)

            jobs = []
            for job in serializer.data:

                job['company'] = company.company
                job['country'] = job['country'].split(',')
                job['city'] = job['city'].split(',')
                job['county'] = job['county'].split(',')

                del job['company_name']

                jobs.append(job)

            return Response(jobs)
        else:
            return Response(status=401)
        
class EditJob(APIView, JobView):
    def post(self, request):
        jobs = self.transformed_jobs(request.data)

        for job in jobs:
            company = get_object_or_404(Company, company=self.transform_data(job.get('company')).title())
            job['company'] = company.id
            
            serializer = JobAddSerializer(data=job, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({'message': 'Job edited'})
    
class DeleteJob(APIView, JobView):
    def post(self, request):
        response = self.update(request.data, 'deleted')
        return response

class PublishJob(APIView, JobView):
    def post(self, request):
        response = self.update(request.data, 'published')
        return response
        
    