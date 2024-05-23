from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100)
    abreviate = models.CharField(max_length=100, unique=True)
    municipality = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name