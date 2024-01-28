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
        
        if isinstance(jobs, list) and len(jobs) > 0:
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

                if _company_serializer.is_valid(raise_exception=True):
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

                    if _job_serializer.is_valid(raise_exception=True):
                        _job_serializer.save()

                        posted_jobs.append(_job_serializer.data)
                    else:
                        return Response(_job_serializer.errors)
                else:
                    return Response(_company_serializer.errors)
    
            return Response(posted_jobs)
        else:
            return Response({'message': 'No jobs provided'}, status=400)
    
    @property
    def delete(self):
        scraper_data = self.request.data

        if isinstance(scraper_data, list) and len(scraper_data) > 0:
            company_obj = Company.objects.filter(company=transform_data(scraper_data[0].get('company').lower())).first()
            database_jobs = Job.objects.filter(company=company_obj.id).values()
            scraper_data = [transform_data(job.get('job_link')) for job in scraper_data]
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
        print(
            company,
            user_companies.filter(company=company.title()).exists()
        )

        if company and user_companies.filter(company=company.title()).exists():
            company = get_object_or_404(Company, company=company.lower())
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
            return Response({'message': 'No company name provided'})
        
class EditJob(APIView):
    def post(self, request):
        jobs = request.data
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
                return Response(JOB_NOT_FOUND)

        return Response({'message': 'Job edited'})
    
class DeleteJob(APIView):
    def post(self, request):
        jobs = request.data
        for job in jobs:
            job_link = transform_data(job.get('job_link'))
            job_obj = Job.objects.get(job_link=job_link)
            if job_obj:
                job_obj.deleted = not job_obj.deleted
                job_obj.save()
            else:
                return Response(JOB_NOT_FOUND)
        
        return Response({'message': 'Job deleted'})

class PublishJob(APIView):
    def post(self, request):
        jobs = request.data
        for job in jobs:
            job_link = transform_data(job.get('job_link'))
            job_obj = Job.objects.get(job_link=job_link)
            if job_obj:
                job_obj.published = not job_obj.published
                job_obj.save()
            else:
                return Response(JOB_NOT_FOUND)
        
        return Response({'message': 'Job published'})
        
    