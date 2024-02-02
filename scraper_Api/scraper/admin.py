from django.contrib import admin
from .models import Scraper, TestLogs, DataSet

admin.site.register(Scraper)
admin.site.register(TestLogs)
admin.site.register(DataSet)
