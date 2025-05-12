from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company']
    search_fields = ['job_title', 'company__company']
    list_filter = ['published']

    def company(self, obj):
        return obj.company.company

