from django.contrib import admin
from .models import Company, DataSet, Source

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company']
    search_fields = ['company']


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['sursa']
    search_fields = ['sursa']

@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    list_display = ['company', 'date', 'data']
    search_fields = ['company__company']
    list_filter = ['date']
    date_hierarchy = 'date'
    ordering = ['date']

