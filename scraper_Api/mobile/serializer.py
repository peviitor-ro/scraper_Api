from rest_framework import serializers
import pysolr
from jobs.models import Job

class JobSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    class Meta:
        model = Job
        fields = '__all__'

    def get_logo(self, obj):
        url = 'http://zimbor.go.ro/solr/auth'

        solr = pysolr.Solr(url)

        results = solr.search('*:*', **{
            'rows': '10000',
        })

        for logo in results.docs:
            if logo.get('id').lower() == obj.company.company.lower():
                return logo.get('logo')

        return None
    
    def get_company_name(self, obj):
        return obj.company.company

