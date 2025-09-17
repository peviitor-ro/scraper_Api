from django.urls import path
from .views import GetJobView, GetTotalJobs, GetCompanies, CheckSavedJobsView

urlpatterns = [
    path('', GetJobView.as_view(), name='jobs'),
    path('companies/', GetCompanies.as_view(), name='companies'),
    path('total/', GetTotalJobs.as_view(), name='total_jobs'),
    path('check-saved/', CheckSavedJobsView.as_view(), name='check_saved_jobs'),
]
