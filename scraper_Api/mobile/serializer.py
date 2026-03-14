from rest_framework import serializers
from jobs.models import Job
from company.models import Company


class JobSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'

    def get_logo(self, obj):
        try:
            if obj.company.source and obj.company.source.image:
                return obj.company.source.image.url
        except Exception:
            return None

        return None

    def get_company_name(self, obj):
        return obj.company.company
    

class JobListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.company for item in data]
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('company',)
        list_serializer_class = JobListSerializer
