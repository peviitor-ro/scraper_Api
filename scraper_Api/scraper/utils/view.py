from rest_framework.views import APIView
from utils.pagination import ScraperPagination
from .serializer import ScraperSerializer
from .constants import SCRAPER_SORT_OPTION
from django.db.models import Q


class GenerivView(APIView):
    """
    A generic view for retrieving a list of scrapers and their endpoints.

    This view returns a list of dictionaries, each containing the name of a scraper
    and its corresponding endpoint URL.

    Example usage:
        GET /generic/ -> Returns a list of scrapers and their endpoints.

    """
    pagination_class = ScraperPagination
    serializer_class = ScraperSerializer

    def get(self, request):

        search_query = request.GET.get("search") or ""
        order_query = request.GET.get("order")

        order_by = SCRAPER_SORT_OPTION.get(order_query)

        model = request.user.scraper.all()

        queryset = model.filter(
            Q(name__icontains=search_query) | Q(
                author__icontains=search_query)
        )

        if order_by:
            queryset = queryset.filter(language=order_by)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(
            queryset=queryset, request=request)
        serializer = self.serializer_class(
            result_page, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)
