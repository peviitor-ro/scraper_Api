import hashlib
from django.db import models
from company.models import Company
import pysolr
import datetime


class Job(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="Company"
    )
    country = models.TextField()
    city = models.TextField(blank=True)
    county = models.TextField(blank=True)
    job_link = models.CharField(max_length=200)
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

    def save(self, *args, **kwargs):
        if self.published:
            self.date = datetime.datetime.now()
        super(Job, self).save(*args, **kwargs)
        solr = pysolr.Solr('http://zimbor.go.ro/solr/shaqodoon')

        if self.published:
            #for testing purposes
            solr.delete(q=f'job_link:"{self.job_link}"')
            solr.commit()

            
            solr.add([
                {
                    "job_link": self.job_link,
                    "job_title": self.job_title,
                    "company": self.company.company,
                    "country": self.country.split(","),
                    "city": self.city.split(","),
                    "county": self.county.split(","),
                    "remote": self.remote.split(","),
                }
            ])
            solr.commit()

    def delete(self, *args, **kwargs):
        solr = pysolr.Solr('http://zimbor.go.ro/solr/shaqodoon')
        q = f'job_link:"{self.job_link}"'
        solr.delete(q=q)
        solr.commit()
        super(Job, self).delete(*args, **kwargs)
