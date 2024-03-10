from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .serializer import CitySerializer

from .models import City
from utils.pagination import CustomPagination

@permission_classes([AllowAny])
class CityViewSet(APIView):
    serializer_class = CitySerializer
    pagination_class = CustomPagination

    def get(self, request):
        search = request.GET.get('search') or ''

        queryset = City.objects.filter(
            Q(name__icontains=search) | Q(county__name__icontains=search)
        )

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(result_page, many=True)

        
        
        return paginator.get_paginated_response(serializer.data)
