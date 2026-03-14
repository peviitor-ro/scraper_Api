from rest_framework.response import Response
from company.models import Company
from django.db import models
import hashlib

class Job(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="jobs"
    )
    country = models.TextField()
    city = models.TextField(blank=True)
    county = models.TextField(blank=True)
    job_link = models.CharField(max_length=1000)
    job_title = models.TextField()
    salary = models.TextField(blank=True, null=True)
    remote = models.CharField(max_length=50, blank=True)
    edited = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.job_title

    @property
    def getJobId(self):
        hash_object = hashlib.md5(self.job_link.encode())
        return hash_object.hexdigest()

    def publish(self):
        self.published = True
        self.save(update_fields=['published'])
        return Response(status=200)

    def unpublish(self):
        self.published = False
        self.save(update_fields=['published'])
        return Response(status=200)
