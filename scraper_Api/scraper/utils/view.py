from rest_framework.views import APIView
from rest_framework.response import Response
from .container import Container
 
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
        host = request.META['HTTP_HOST']
        response = [
            {
                'name': scraper,
                'endpoint': f'https://{host}/scraper/{scraper}/'
            } for scraper in scrapers
        ]
        return Response(response)
