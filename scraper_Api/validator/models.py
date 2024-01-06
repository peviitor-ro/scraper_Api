from collections.abc import Iterable
from django.db import models
import hashlib

class Company(models.Model):
    company = models.CharField(max_length=50)

    def __str__(self):
        return self.company

class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='Company')
    country = models.TextField()
    city = models.TextField(blank=True)
    county = models.TextField(blank=True)
    job_link = models.CharField(max_length=200)
    job_title = models.TextField()
    remote = models.CharField(max_length=50, blank=True)
    edited = models.BooleanField(default=False)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.job_title
    
    @property
    def getJobId(self):
        hash_object = hashlib.md5(self.job_link.encode())
        return hash_object.hexdigest()