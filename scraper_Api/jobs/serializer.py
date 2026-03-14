from rest_framework import serializers
from django.db import transaction
from datetime import datetime
from .models import Job


class JobAddSerializer(serializers.ModelSerializer):
    job_id = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    salary = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Job
        fields = ['job_link', 'job_title', 'company', 'country',
                  'city', 'county', 'salary', 'salary_min', 'salary_max', 'remote', 'job_id', 'company_name']

    def validate(self, attrs):
        salary = attrs.pop('salary', None)

        if salary and attrs.get('salary_min') is None and attrs.get('salary_max') is None:
            salary_parts = [part.strip() for part in str(salary).replace('RON', '').replace('ron', '').split('-')]
            numeric_parts = []

            for part in salary_parts:
                digits = ''.join(character for character in part if character.isdigit())
                if digits:
                    numeric_parts.append(int(digits))

            if len(numeric_parts) >= 1:
                attrs['salary_min'] = numeric_parts[0]

            if len(numeric_parts) >= 2:
                attrs['salary_max'] = numeric_parts[1]

        if attrs.get('salary_min') is not None and attrs.get('salary_max') is not None:
            if attrs['salary_min'] > attrs['salary_max']:
                raise serializers.ValidationError('salary_min cannot be greater than salary_max')

        return attrs

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
            instance.save()
            return instance


class GetJobSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    posted = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id','job_link', 'job_title', 'company', 'country', 'city',
                  'county', 'salary_min', 'salary_max', 'remote', 'edited', 'published', 'posted', 'company_name']

    def get_company_name(self, obj):
        return obj.company.company

    def get_posted(self, obj):
        try:
            posted = datetime.strftime(obj.date, '%Y-%m-%d')
            return posted
        except Exception:
            return False
