from django.db import models
from datetime import datetime

class Company(models.Model):
    company = models.TextField(max_length=50)
    scname = models.CharField(max_length=50, blank=True)
    website = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company
    

class DataSet (models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='CompanyData')
    date = models.DateField(default=datetime.now())
    data = models.IntegerField()


