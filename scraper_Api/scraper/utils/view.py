from rest_framework.views import APIView
from rest_framework.response import Response
from scraper_Api.settings import DEBUG
 
class GenerivView(APIView):
    """
    A generic view for retrieving a list of scrapers and their endpoints.

    This view returns a list of dictionaries, each containing the name of a scraper
    and its corresponding endpoint URL.

    Example usage:
        GET /generic/ -> Returns a list of scrapers and their endpoints.

    """

    def get(self, request):
        scrapers = request.user.scraper.all().values_list('name', flat=True)
        protocol = 'http' if DEBUG else 'https'
        host = request.META['HTTP_HOST']
        response = [
            {
                'name': scraper,
                'endpoint': f'{protocol}://{host}/scraper/{scraper}/'
            } for scraper in scrapers
        ]
        return Response(response)
