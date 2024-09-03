from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.pagination import CustomPagination
from .serializer import JobSerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from jobs.models import Job

@permission_classes([AllowAny])
class GetJobView(APIView):
    serializer_class = JobSerializer
    pagination_class = CustomPagination
    def get(self, request):
        search_query = request.GET.get("search") or None

        if not search_query:
            queryset = Job.objects.all().filter(published=True)
        else:
            queryset = Job.objects.filter(
                Q(job_title__icontains=search_query)
            ).filter(published=True)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
@permission_classes([AllowAny])
class GetTotalJobs(APIView):
    def get(self, _):
        total_jobs = Job.objects.filter(published=True).count()
        return Response({"total": total_jobs})

