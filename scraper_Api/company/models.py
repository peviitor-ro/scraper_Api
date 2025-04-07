from django.db import models
from django.utils.timezone import datetime
import os


class Source(models.Model):
    """
    Sursa is a Django model representing a source with an associated image.
    Attributes:
        sursa (CharField): A unique name for the source, limited to 50 characters.
        image (ImageField): An optional image associated with the source, stored in the 'images/' directory.
    Methods:
        __str__(): Returns the string representation of the source (its name).
        delete(using=None, keep_parents=False): Deletes the model instance and removes the associated image file
            from the filesystem if it exists.
    """
    sursa = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.sursa

    def delete(self, using=None, keep_parents=False):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)

        super().delete(using=using, keep_parents=keep_parents)

class Company(models.Model):
    """
    Represents a company.

    Attributes:
        company (TextField): The name of the company.
        scname (CharField): The short name or abbreviation of the company (optional).
        website (CharField): The website URL of the company (optional).
        description (TextField): A description of the company (optional).
    """

    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='company', null=True, blank=True
    )
    company = models.TextField(max_length=300)
    scname = models.CharField(max_length=50, blank=True)
    website = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company
    

class DataSet(models.Model):
    """
    Represents a data set associated with a company.

    Attributes:
        company (Company): The company associated with the data set.
        date (DateField): The date of the data set.
        data (IntegerField): The data value of the data set.
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='CompanyData')
    date = models.DateField(default=datetime.now())
    data = models.IntegerField()

    def __str__(self):
        return self.company.company


