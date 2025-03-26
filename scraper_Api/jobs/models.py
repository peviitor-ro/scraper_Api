import hashlib
from django.db import models
from company.models import Company
from dotenv import load_dotenv
import os
from rest_framework.response import Response
from requests.auth import HTTPBasicAuth
import pysolr
import re
import html
from django.db.models.signals import pre_delete
from django.dispatch import receiver

load_dotenv()
DATABASE_SOLR = os.getenv("DATABASE_SOLR")


class Job(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="jobs"
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
    
    @staticmethod
    def _escape_solr_query(value):
        value = html.escape(value)  
        special_chars = r'(\+|\-|\&|\||\!|\(|\)|\{|\}|\[|\]|\^|\"|\~|\*|\?|\:|\\|=)'
        escaped_value = re.sub(special_chars, r'\\\1', value)
        return escaped_value
        
    def delete(self, *args, **kwargs):
        url = DATABASE_SOLR + "/solr/jobs"
        username = os.getenv("DATABASE_SOLR_USERNAME")
        password = os.getenv("DATABASE_SOLR_PASSWORD")

        solr = pysolr.Solr(url=url, auth=HTTPBasicAuth(username, password), timeout=5)

        job_link_safe = self._escape_solr_query(self.job_link)

        solr.delete(q=f'job_link:"{job_link_safe}"')
        solr.commit(expungeDeletes=True)

        super(Job, self).delete(*args, **kwargs)

    def publish(self):
        city = set(x.strip()
                   for x in self.city.split(","))

        url = DATABASE_SOLR + "/solr/jobs"
        username = os.getenv("DATABASE_SOLR_USERNAME")
        password = os.getenv("DATABASE_SOLR_PASSWORD")

        try:
            solr = pysolr.Solr(url=url, auth=HTTPBasicAuth(username, password), timeout=5)
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
        
# Delete related jobs when a company is deleted
@receiver(pre_delete, sender=Company)
def delete_related_jobs(sender, instance, **kwargs):
    jobs = Job.objects.filter(company=instance)
    for job in jobs:
        job.delete()

    