from django.contrib import admin
from .models import Scraper, TestLogs

admin.site.register(Scraper)
admin.site.register(TestLogs)
