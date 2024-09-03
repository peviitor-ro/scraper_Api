from django.contrib import admin
from .models import Company, DataSet

admin.site.register(DataSet)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company']
    search_fields = ['company']

