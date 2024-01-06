from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import JobAddSerializer, CompanySerializer
from .models import Job, Company
from django.shortcuts import get_object_or_404
import json


def transform_data(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, list):
        data_string = ",".join(data)
        return data_string
    else:
        return ""


class ScraperValidator(APIView):
    def post(self, request):
        jobs = request.data
        posted_jobs = []

        for job in jobs:
            job_link = transform_data(job.get('job_link'))
            job_title = transform_data(job.get('job_title'))
            company = transform_data(job.get('company')).lower()
            country = transform_data(job.get('country'))
            city = transform_data(job.get('city'))
            county = transform_data(job.get('county'))
            remote = transform_data(job.get('remote'))

            _company_serializer = CompanySerializer(
                data={'company': company})

            if _company_serializer.is_valid():
                instance = _company_serializer.save()
                
                job_element = {
                    'job_link': job_link,
                    'job_title': job_title,
                    'company': instance.id,
                    'country': country,
                    'city': city,
                    'county': county,
                    'remote': remote,
                }

                _job_serializer = JobAddSerializer(data=job_element)

                if _job_serializer.is_valid():
                    _job_serializer.save()

                    posted_jobs.append(_job_serializer.data)
    
        return Response(posted_jobs)
    
    @property
    def delete(self):
        scraper_data = self.request.data
        company_obj = Company.objects.filter(company=transform_data(scraper_data[0].get('company').lower())).first()
        database_jobs = Job.objects.filter(company=company_obj.id).values()
        scraper_data = [transform_data(job.get('job_link')) for job in scraper_data]
        database_jobs = [job.get('job_link') for job in database_jobs]
        to_delete = [job for job in database_jobs if job not in scraper_data]
        
        for job in to_delete:
            Job.objects.filter(job_link=job).delete()
    

class GetCompanyData(APIView):
    def post(self, request):
        company = request.data.get('company')

        if company:
            company = get_object_or_404(Company, company=company.lower())
            jobs_objects = Job.objects.filter(company=company.id)
            serializer = JobAddSerializer(jobs_objects, many=True)

            jobs = []
            for job in serializer.data:
                job['company'] = company.company
                job['country'] = job['country'].split(',')
                job['city'] = job['city'].split(',')
                job['county'] = job['county'].split(',')

                del job['job_id']
                del job['company_name']

                jobs.append(job)

            return Response(jobs)
        else:
            return Response({'message': 'No company name provided'})
        
class EditJob(APIView):
    def post(self, request):
        print(request.data)
        jobs = request.data
        print(type(jobs))
        for job in jobs:
            job_link = transform_data(job.get('job_link'))
            job_title = transform_data(job.get('job_title'))
            country = transform_data(job.get('country'))
            city = transform_data(job.get('city'))
            county = transform_data(job.get('county'))
            remote = transform_data(job.get('remote'))
            
            
            job_obj = Job.objects.get(job_link=job_link)
            if job_obj:      
                job_obj.job_title = job_title
                job_obj.country = country
                job_obj.city = city
                job_obj.county = county
                job_obj.remote = remote
                job_obj.edited = True
                job_obj.save()
            else:
                return Response({'message': 'Job not found'})

        
        return Response({'message': 'Job edited'})
        
    