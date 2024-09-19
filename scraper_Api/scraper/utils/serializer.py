from rest_framework import serializers
from scraper_Api.settings import DEBUG
from ..models import Scraper


class ScraperSerializer(serializers.ModelSerializer):
    endpoint = serializers.SerializerMethodField()

    class Meta:
        model = Scraper
        fields = ['name', 'language', 'endpoint']

    def get_endpoint(self, scraper):
        request = self.context.get('request')
        protocol = 'http' if DEBUG else 'https'
        host = request.get_host()

        return f'{protocol}://{host}/scraper/{scraper}/'
