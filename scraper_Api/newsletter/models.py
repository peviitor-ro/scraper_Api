from django.db import models


class Users(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    email = models.ForeignKey(Users, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50, blank=True)
    job_type = models.CharField(max_length=10, blank=True)
    company = models.CharField(max_length=50, blank=True)


    def __str__(self):
        return self.email.email

    def clean_data(self):
        self.job_type = ''
        self.job_title = ''
        self.company = ''
        self.city = ''



