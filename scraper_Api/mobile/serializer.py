from rest_framework import serializers
from requests.auth import HTTPBasicAuth
import pysolr
from jobs.models import Job
from company.models import Company
from dotenv import load_dotenv
import os
load_dotenv()


class JobSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'

    def get_logo(self, obj):
        url = os.getenv("DATABASE_SOLR") + '/solr/auth'
        username = os.getenv("DATABASE_SOLR_USERNAME")
        password = os.getenv("DATABASE_SOLR_PASSWORD")

        try:
            solr = pysolr.Solr(url, auth=HTTPBasicAuth(username, password), timeout=5)
            company = str(obj.company)

            query = f'id:{company} OR id:{company.lower()} OR id:{company.upper()} OR id:{company.capitalize()}'
            results = solr.search(query, **{
                'rows': '1',
            })

            return results.docs[0].get('logo')
        except Exception:
            return None

    def get_company_name(self, obj):
        return obj.company.company
    

class JobListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.company for item in data]
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('company')
        list_serializer_class = JobListSerializer
    

