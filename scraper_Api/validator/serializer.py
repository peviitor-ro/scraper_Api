from .models import Job, Company
from rest_framework import serializers
from django.db import transaction
from users.models import CustomUser
import requests

class CompanySerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = ['company', 'scname', 'website', 'logo']

    def create(self, validated_data):
        instance , create = Company.objects.get_or_create(**validated_data)

        if create:
            superusers = CustomUser.objects.filter(is_superuser=True)
            for user in superusers:
                user.company.add(instance)
                user.save()
        return instance
    
    def get_logo(self, obj):
        logo = requests.get(f'https://logo.clearbit.com/{obj.website}')
        if logo.status_code == 200:
            return logo.url

class JobAddSerializer(serializers.ModelSerializer):
    job_id = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['job_link', 'job_title', 'company', 'country', 'city', 'county', 'remote', 'job_id', 'company_name']
        

    def create(self, validated_data):
        try:
            with transaction.atomic():
                instance , create = Job.objects.update_or_create(job_link = validated_data['job_link'], defaults = validated_data)

                if not create and not instance.edited:
                    instance.save()
                elif create:
                    instance.save()
                else:
                    raise ValueError('Job already exists')
        except ValueError:
            job = Job.objects.get(job_link = validated_data['job_link'])
            return job

        return instance
    
    def get_job_id(self, obj):
        return obj.getJobId
    
    def get_company_name(self, obj):
        return obj.company.company
    
class GetJobSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    class Meta:
        model = Job
        fields = ['job_link', 'job_title', 'company', 'country', 'city', 'county', 'remote', 'edited', 'published', 'deleted', 'company_name']

    def get_company_name(self, obj):
        return obj.company.company
    

