from django.db import models
from django.urls import reverse


class Scraper (models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class TestLogs (models.Model):

    scraper = models.ForeignKey(Scraper, on_delete=models.CASCADE, related_name='Scraper')
    test_date = models.DateTimeField(auto_now_add=True)
    test_result = models.TextField(blank=True, null=True)
    is_success = models.CharField(max_length=10)

    def __str__(self):
        return self.scraper.name + " " + str(self.test_date)
    
