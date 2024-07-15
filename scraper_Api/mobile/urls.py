from django.urls import path
from .views import GetJobView, GetTotalJobs

urlpatterns = [
    path('', GetJobView.as_view(), name='jobs'),
    path('total/', GetTotalJobs.as_view(), name='total_jobs')
]
