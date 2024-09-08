import hashlib
from django.db import models
from company.models import Company
from django.utils.timezone import datetime
from dotenv import load_dotenv
import os
from rest_framework.response import Response
import pysolr

load_dotenv()
DATABASE_SOLR = os.getenv("DATABASE_SOLR")


class Job(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="Company"
    )
    country = models.TextField()
    city = models.TextField(blank=True)
    county = models.TextField(blank=True)
    job_link = models.CharField(max_length=300)
    job_title = models.TextField()
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

    def delete(self, *args, **kwargs):
        url = DATABASE_SOLR + "/solr/jobs"
        solr = pysolr.Solr(url=url)
        solr.delete(q=f'job_link:"{self.job_link}"')
        solr.commit(expungeDeletes=True)

        super(Job, self).delete(*args, **kwargs)

    def publish(self):
        city = set(x.strip().split(" ")[0]
                   for x in self.city.split(","))
        url = DATABASE_SOLR + "/solr/jobs"

        try:
            solr = pysolr.Solr(url=url)
            solr.add([
                {
                    "job_link": self.job_link,
                    "job_title": self.job_title,
                    "company": self.company.company,
                    "country": self.country.split(","),
                    "city": list(city),
                    "county": self.county.split(","),
                    "remote": self.remote.split(","),
                }
            ])

            solr.commit(expungeDeletes=True)
            return Response(status=200)
        except pysolr.SolrError as e:
            return Response(status=400, data=e)
