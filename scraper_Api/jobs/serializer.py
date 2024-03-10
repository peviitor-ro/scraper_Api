from rest_framework import serializers
from django.db import transaction
from datetime import datetime
from .models import Job


class JobAddSerializer(serializers.ModelSerializer):
    job_id = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['job_link', 'job_title', 'company', 'country',
                  'city', 'county', 'remote', 'job_id', 'company_name']

    def create(self, validated_data):

        with transaction.atomic():
            instance, _ = Job.objects.get_or_create(
                job_link=validated_data['job_link'], defaults=validated_data)
            instance.save()
            return instance

    def get_job_id(self, obj):
        return obj.getJobId

    def get_company_name(self, obj):
        return obj.company.company


class JobAEditSerializer(JobAddSerializer):
    def create(self, validated_data):
        with transaction.atomic():
            instance, _ = Job.objects.update_or_create(
                job_link=validated_data['job_link'], defaults=validated_data)
            instance.edited = True
            instance.save()
            return instance


class GetJobSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    posted = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['job_link', 'job_title', 'company', 'country', 'city',
                  'county', 'remote', 'edited', 'published', 'posted', 'company_name']

    def get_company_name(self, obj):
        return obj.company.company
    
    def get_posted(self, obj):
        try:
            posted = datetime.strftime(obj.date, '%Y-%m-%d')
            return posted
        except Exception:
            return False
