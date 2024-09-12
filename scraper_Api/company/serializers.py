from rest_framework import serializers
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

    class Meta:
        model = Company
        fields = ['company', 'scname', 'website',
                  'description', 'logo', 'jobsCount', 'published_jobs', 'have_access']

    def create(self, validated_data):
        instance, create = Company.objects.get_or_create(**validated_data)

        if create:
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
    
    

    def get_logo(self, obj):
        
        url = os.getenv("DATABASE_SOLR") + '/solr/auth'

        try:
            solr = pysolr.Solr(url)
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
