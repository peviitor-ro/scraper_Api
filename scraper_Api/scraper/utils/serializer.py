from rest_framework import serializers
from ..models import Scraper


class ScraperSerializer(serializers.ModelSerializer):
    endpoint = serializers.SerializerMethodField()

    class Meta:
        model = Scraper
        fields = ['name', 'language', 'endpoint']

    def get_endpoint(self, scraper):
        request = self.context.get('request')
        protocol = 'http' if request.META.get('HTTP_HOST') else 'https'
        host = request.get_host()

        return f'{protocol}://{host}/scraper/{scraper}/'
