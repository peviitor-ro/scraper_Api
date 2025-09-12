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
        validate = serializers.ChoiceField(choices=[('remote', 'remote'), ('on-site', 'on-site'), ('hybrid', 'hybrid')],
                                           allow_blank=True)
        remote_elements = validated_data['remote'].split(',')

        for element in remote_elements:
            validate.to_internal_value(element.lower())

        instance, _ = Job.objects.get_or_create(
            job_link=validated_data['job_link'], defaults=validated_data)
        if not instance.edited:
            for key, value in validated_data.items():
                setattr(instance, key, value)
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

            if instance.published:
                instance.delete()
                instance.publish()
            instance.save()
            return instance


class GetJobSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    posted = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id','job_link', 'job_title', 'company', 'country', 'city',
                  'county', 'remote', 'edited', 'published', 'posted', 'company_name']

    def get_company_name(self, obj):
        return obj.company.company

    def get_posted(self, obj):
        try:
            posted = datetime.strftime(obj.date, '%Y-%m-%d')
            return posted
        except Exception:
            return False
