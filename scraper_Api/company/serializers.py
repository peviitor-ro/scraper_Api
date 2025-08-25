from rest_framework import serializers
from requests.auth import HTTPBasicAuth
import pysolr
from users.models import CustomUser
from .models import Company, DataSet
from jobs.models import Job

from dotenv import load_dotenv
import os
load_dotenv()

class CompanySerializer(serializers.ModelSerializer):
    jobsCount = serializers.SerializerMethodField()
    published_jobs = serializers.SerializerMethodField()
    have_access = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    source_name = serializers.SerializerMethodField()
    source_logo = serializers.SerializerMethodField()


    class Meta:
        model = Company
        fields = ['company', 'scname', 'website',
                  'description', 'logo', 'source','jobsCount', 'published_jobs', 'have_access', 'source_name', 'source_logo']

    def create(self, validated_data):
        instance = Company.objects.filter(**validated_data).first()
        if not instance:
            instance = Company.objects.create(**validated_data)
            superusers = CustomUser.objects.filter(is_superuser=True)
            for user in superusers:
                user.company.add(instance)
                user.save()
        return instance
    
    def get_have_access(self, obj):
        request = self.context.get('request')
        user = request.user
        return user.company.filter(id=obj.id).exists()

    def get_jobsCount(self, obj):
        total_jobs = Job.objects.filter(company=obj.id).count()
        return total_jobs
    
    def get_published_jobs(self, obj):
        published_jobs = Job.objects.filter(company=obj.id, published=True).count()
        return published_jobs
    
    def get_source_name(self, obj):
        try:
            return obj.source.sursa
        except Exception:
            return None
    def get_source_logo(self, obj):
        try:
            return obj.source.image.url
        except Exception:
            return None

    

    def get_logo(self, obj):
        
        url = os.getenv("DATABASE_SOLR") + '/solr/auth'
        username = os.getenv("DATABASE_SOLR_USERNAME")
        password = os.getenv("DATABASE_SOLR_PASSWORD")

        try:
            solr = pysolr.Solr(url, auth=HTTPBasicAuth(username, password), timeout=60)
            company = obj.company
            
            query = f'id:{company} OR id:{company.lower()} OR id:{company.upper()} OR id:{company.capitalize()}'
            results = solr.search(query, **{
                'rows': '1',
            })

            return results.docs[0].get('logo')
        except Exception:
            return None


class DataSetSerializer(serializers.ModelSerializer):
    formated_date = serializers.SerializerMethodField()

    class Meta:
        model = DataSet
        fields = ['data', 'formated_date']

    def get_formated_date(self, obj):
        months = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "July",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec"
        }
        return str(obj.date.day) + " " + months[obj.date.month]
