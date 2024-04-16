from rest_framework import serializers
import pysolr
from users.models import CustomUser
from .models import Company, DataSet
from jobs.models import Job

class CompanySerializer(serializers.ModelSerializer):
    jobsCount = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['company', 'scname', 'website',
                  'description', 'logo', 'jobsCount']

    def create(self, validated_data):
        instance, create = Company.objects.get_or_create(**validated_data)

        if create:
            superusers = CustomUser.objects.filter(is_superuser=True)
            for user in superusers:
                user.company.add(instance)
                user.save()
        return instance

    def get_jobsCount(self, obj):
        total_jobs = Job.objects.filter(company=obj.id).count()
        return total_jobs

    def get_logo(self, obj):
        url = 'http://zimbor.go.ro/solr/auth'

        solr = pysolr.Solr(url)

        results = solr.search('*:*', **{
            'rows': '10000',
        })

        logo = [logo.get('logo')[0] for logo in results.docs if logo.get(
            'id').lower() == obj.company.lower()]
        
        return logo[0] if logo else None


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
